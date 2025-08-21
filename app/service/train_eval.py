# scripts/train_eval.py
import os, math
import argparse
import numpy as np
from collections import defaultdict

from datato import load_ei_rows_from_csv   # 네가 방금 수정한 datato.py 버전
from train_xgb import EIBaseline, train_ei_residual, predict_from_ei
import joblib

# ---------------------------
# 1) 데이터 로드
# ---------------------------
def load_rows(csv_path: str, encoding="utf-8-sig"):
    rows = load_ei_rows_from_csv(csv_path, encoding=encoding)
    if not rows:
        raise RuntimeError("학습 데이터가 비어있습니다.")
    print(f"[INFO] Loaded {len(rows)} rows from {csv_path}")
    return rows

# ---------------------------
# 2) 거리 콜백 (distance_provider)
#    - 프로덕션에선 GeoPandas 라우터를 쓰지만,
#      스모크 테스트에선 CSV의 distance_km을 그대로 사용.
#    - 중복(origin,dest)은 평균으로 집계.
# ---------------------------
def make_distance_provider_from_csv(rows):
    agg = defaultdict(list)
    for r in rows:
        key = (r.origin.strip().upper(), r.dest.strip().upper())
        agg[key].append(float(r.distance_km))
    mean_km = {k: float(np.mean(v)) for k, v in agg.items()}
    def provider(origin: str, dest: str) -> float:
        k = (origin.strip().upper(), dest.strip().upper())
        if k not in mean_km:
            raise KeyError(f"distance not found in CSV for {origin}->{dest}")
        return mean_km[k] / 1.852  # km -> nm
    return provider

# ---------------------------
# 3) 베이스라인 설정
#    (값은 예시. 네 프로젝트 기준으로 맞춰 조정 가능)
# ---------------------------
def make_baseline():
    return EIBaseline(
        ef_ton_per_ton=3.114,   # HFO 예시
        reserve_ratio=0.05,
        sfoc_g_per_kwh=180.0,   # 예시
        speed_kn=18.0,          # 예시
        alpha=1.0,
        teu_ref=8000.0          # 데이터 규모에 맞게
    )

# ---------------------------
# 4) 학습 및 평가
#    train_ei_residual 내부에서 KFold로
#    Baseline vs Residual의 MAE/RMSE를 출력해줌.
# ---------------------------
def train_model(rows):
    baseline = make_baseline()
    pack = train_ei_residual(rows, baseline, fuel_name="HFO")
    return pack

# ---------------------------
# 5) 샘플 추론
# ---------------------------
def sample_predict(pack, dp, origin, dest, teu_loaded=8000):
    pred = predict_from_ei(
        pack=pack,
        origin=origin,
        dest=dest,
        teu_loaded=float(teu_loaded),
        distance_provider=dp
    )
    print(f"[PRED] {origin} -> {dest}")
    for k, v in pred.items():
        print(f"  {k}: {v}")
    return pred

# ---------------------------
# 6) 모델 저장/로드 (joblib)
# ---------------------------
def save_model(pack, path="models/ei_residual.joblib"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(pack, path)
    print(f"[INFO] Saved model to {path}")

def load_model(path="models/ei_residual.joblib"):
    return joblib.load(path)

# ---------------------------
# CLI
# ---------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/train.csv", help="학습 CSV 경로 (origin,dest,emission,distance_km)")
    ap.add_argument("--encoding", default="utf-8-sig")
    ap.add_argument("--save", default="models/ei_residual.joblib")
    ap.add_argument("--predict-origin", default=None)
    ap.add_argument("--predict-dest", default=None)
    ap.add_argument("--teu", type=float, default=8000.0)
    args = ap.parse_args()

    rows = load_rows(args.csv, encoding=args.encoding)
    dp = make_distance_provider_from_csv(rows)

    # 학습 (KFold 성능 출력될 것)
    pack = train_model(rows)

    # 저장/재로딩 테스트
    save_model(pack, args.save)
    pack2 = load_model(args.save)

    # 샘플 추론: 인자를 주면 그 구간으로, 아니면 첫 행으로
    if args.predict_origin and args.predict_dest:
        origin, dest = args.predict_origin, args.predict_dest
    else:
        origin, dest = rows[0].origin, rows[0].dest

    sample_predict(pack2, dp, origin, dest, teu_loaded=args.teu)

if __name__ == "__main__":
    main()
