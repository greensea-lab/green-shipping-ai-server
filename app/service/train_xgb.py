# model_ei_residual.py
import math
from dataclasses import dataclass
from typing import List, Dict, Callable, Tuple
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error

from app.service.datato import EIRow

DistanceProvider = Callable[[str, str], float]  # (origin, dest) -> distance_nm

def nm_to_km(x: float) -> float: return x * 1.852

# --- 베이스라인 파라미터(연료 1종 가정; 여러 연료면 dict로 확장) ---
@dataclass
class EIBaseline:
    ef_ton_per_ton: float   # ton CO2 / ton fuel (DB에서)
    reserve_ratio: float    # r
    sfoc_g_per_kwh: float   # g/kWh
    speed_kn: float         # kn
    alpha: float            # k 스케일
    teu_ref: float          # 학습 기준 TEU (데이터에 TEU가 없으므로 고정)

    def ei0(self) -> float:
        """
        EI_0 [kg / TEU·km] = EF*(1-r)*SFOC*alpha*v_kn^2 / (1852 * TEU_ref)
        (SFOC[g/kWh] → kg 변환은 1e-3 이지만 계수 전체에서 1852/1e6 상쇄되어 최종 단위는 kg/TEU·km)
        """
        return (self.ef_ton_per_ton * (1 - self.reserve_ratio)
                * self.sfoc_g_per_kwh * self.alpha * (self.speed_kn ** 2)) / (1852.0 * self.teu_ref)

@dataclass
class TrainedEIResidual:
    baseline: EIBaseline
    model: XGBRegressor
    fuel_name: str  # 표시용

# --- 특징: 거리 기반(필요시 더미/국가 코드 추가 가능) ---
def _row_to_features(distance_km: float) -> np.ndarray:
    return np.array([distance_km, math.log(max(distance_km, 1e-6))], dtype=np.float32)

def train_ei_residual(
    rows: List[EIRow],
    baseline: EIBaseline,
    fuel_name: str = "HFO",
    random_state: int = 42
) -> TrainedEIResidual:
    X = np.vstack([_row_to_features(r.distance_km) for r in rows]).astype(np.float32)
    y = np.array([r.ei_per_teu_km for r in rows], dtype=np.float32)

    ei0 = float(baseline.ei0())  # 상수
    residual = y - ei0

    model = XGBRegressor(
        booster="gbtree",
        n_estimators=400,
        max_depth=2,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        min_child_weight=5.0,
        reg_lambda=6.0,
        reg_alpha=0.5,
        objective="reg:squarederror",
        random_state=random_state
    )

    kf = KFold(n_splits=min(5, max(2, len(rows))), shuffle=True, random_state=random_state)
    mae_b, rmse_b, mae_f, rmse_f = [], [], [], []
    for tr, va in kf.split(X):
        # baseline only
        y0 = np.full_like(residual[va], ei0)
        y_va = y[va]
        mae_b.append(mean_absolute_error(y_va, y0))
        rmse_b.append(mean_squared_error(y_va, y0) ** 0.5)
        # baseline + residual
        model.fit(X[tr], residual[tr], eval_set=[(X[va], residual[va])], verbose=False)
        r_hat = model.predict(X[va])
        y_hat = y0 + r_hat
        mae_f.append(mean_absolute_error(y_va, y_hat))
        rmse_f.append(mean_squared_error(y_va, y_hat) ** 0.5)
    print(f"[Baseline]  MAE={np.mean(mae_b):.3f}, RMSE={np.mean(rmse_b):.3f} (kg/TEU·km)")
    print(f"[+Residual] MAE={np.mean(mae_f):.3f}, RMSE={np.mean(rmse_f):.3f}")

    # 최종 적합
    model.fit(X, residual, verbose=False)
    return TrainedEIResidual(baseline=baseline, model=model, fuel_name=fuel_name)

# --- 추론: EI → CO2 → FC (항해그래프 콜백 필수) ---
def predict_from_ei(
    pack: TrainedEIResidual,
    origin: str,
    dest: str,
    teu_loaded: float,
    *,
    distance_provider: DistanceProvider
) -> Dict[str, float]:
    if teu_loaded <= 0:
        raise ValueError("teu_loaded > 0 필요")

    d_nm = float(distance_provider(origin, dest))
    if not np.isfinite(d_nm) or d_nm <= 0:
        raise ValueError(f"항해그래프가 비정상 거리 반환: {d_nm}")
    d_km = nm_to_km(d_nm)

    ei0 = pack.baseline.ei0()
    r_hat = float(pack.model.predict(_row_to_features(d_km).reshape(1, -1))[0])
    ei = max(0.0, ei0 + r_hat)  # kg/TEU·km

    co2_ton = (ei * d_km * teu_loaded) / 1000.0
    denom = pack.baseline.ef_ton_per_ton * (1 - pack.baseline.reserve_ratio)
    if denom <= 0:
        raise ValueError("EF*(1-r) <= 0")
    fc_ton = co2_ton / denom

    return {
        "distance_km": d_km,
        "ei_kg_per_teu_km": ei,
        "co2_ton": co2_ton,
        "fc_ton": fc_ton
    }
