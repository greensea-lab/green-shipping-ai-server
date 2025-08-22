# greenshipping/models/train_xgb.py
from __future__ import annotations
import os, argparse, joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from xgboost import XGBRegressor

FEATURES = [
    "distance_nm","speed_knots","sfoc_g_per_kwh","k","x_dist_spd2",
    "speed_ratio","speed_ratio_cu","dwt_ton","gt","engine_power_kw",
    "cap_teu","cap_dwt","cap_m3"
]

def load_dataset(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    for c in FEATURES + ["y_fc_ton"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def train(df: pd.DataFrame, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)

    if df["y_fc_ton"].notna().sum() < 50:
        raise SystemExit("학습용 라벨이 부족합니다(>=50 권장). 라벨 CSV를 준비하거나 후속 수집 필요.")

    # 결측 처리 단순안: 결측은 0으로(모델이 중요도 낮은 피처는 무시). 더 좋은 방법은 imputer 사용.
    X = df[FEATURES].fillna(0.0).values
    y = df["y_fc_ton"].values
    groups = df["imo"] if "imo" in df.columns else np.arange(len(df))

    gkf = GroupKFold(n_splits=5)
    maes, mapes = [], []

    model = XGBRegressor(
        n_estimators=600,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=0
    )

    for fold, (tr, va) in enumerate(gkf.split(X, y, groups)):
        model.fit(X[tr], y[tr], eval_set=[(X[va], y[va])], verbose=False)
        p = model.predict(X[va])
        maes.append(mean_absolute_error(y[va], p))
        mapes.append(mean_absolute_percentage_error(y[va], p))

    print(f"[CV] MAE: {np.mean(maes):.4f}  MAPE: {np.mean(mapes)*100:.2f}%")

    # 전체로 다시 적합 후 저장
    model.fit(X, y)
    joblib.dump({"model": model, "features": FEATURES}, os.path.join(out_dir, "xgb_fc.joblib"))
    print(f"[OK] model saved: {os.path.join(out_dir, 'xgb_fc.joblib')}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    df = load_dataset(a.dataset)
    train(df, a.out)
