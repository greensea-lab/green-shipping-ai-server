# predict.py (revised)
from typing import Dict, Tuple, Optional, Callable
from app.service.data_set import TrainRow, nm_to_km, estimate_rfc, row_to_features
from app.service.train_xgb import TrainedFCModel

def predict_fc_co2_ei(
    model_pack: TrainedFCModel,
    ports_db: Dict[str, Tuple[float, float]],   # 유지(콜백 내부에서 쓸 수 있음)
    origin: str,
    dest: str,
    teu_loaded: float,
    fuel: str,
    *,
    distance_nm: Optional[float] = None,        # 제공 시 우선 사용
    distance_km: Optional[float] = None,        # 제공 시 우선 사용
    distance_provider: Optional[Callable[[str, str], float]] = None  # 항해그래프 콜백(반환: nm)
) -> Dict[str, float]:
    """
    거리 해석 우선순위:
      1) distance_nm 인자
      2) distance_km 인자
      3) distance_provider(origin, dest)  # 항해그래프 필수
      -> 그 외(미제공) 에러 발생 (대권거리 사용 금지)
    """
    if teu_loaded <= 0:
        raise ValueError("teu_loaded > 0 이어야 합니다.")
    fuel_up = fuel.strip().upper()

    # --- 거리 결정 (직선거리 사용 금지) ---
    if distance_nm is not None:
        D_nm = float(distance_nm)
    elif distance_km is not None:
        D_nm = float(distance_km) / 1.852
    elif distance_provider is not None:
        D_nm = float(distance_provider(origin, dest))  # 항해그래프 결과(nm)
    else:
        raise ValueError(
            "거리 소스가 없습니다. distance_nm 또는 distance_km를 제공하거나 "
            "distance_provider(항해그래프 콜백)를 넘겨주세요."
        )
    if D_nm <= 0:
        raise ValueError(f"유효하지 않은 거리(nm): {D_nm}")
    D_km = nm_to_km(D_nm)

    # --- 특징 벡터 구성 & FC 예측 ---
    dummy = TrainRow(D_nm=D_nm, fuel=fuel_up, teu_loaded=teu_loaded, fc_obs_ton=0.0)
    x = row_to_features(dummy, model_pack.fuel_vocab, model_pack.use_teu).reshape(1, -1)
    fc = float(model_pack.model.predict(x)[0])  # ton

    # --- CO2 ---
    if fuel_up not in model_pack.ef_table:
        raise KeyError(f"EF 미정의 연료: '{fuel_up}'")
    ef = model_pack.ef_table[fuel_up]
    rfc = estimate_rfc(fc, model_pack.reserve_ratio)
    co2_ton = ef * max(0.0, fc - rfc)

    # --- EI ---
    ei = (co2_ton * 1000.0) / (D_km * teu_loaded)

    return {
        "distance_nm": D_nm,
        "distance_km": D_km,
        "fc_ton": fc,
        "co2_ton": co2_ton,
        "ei_kg_per_teu_km": ei
    }
