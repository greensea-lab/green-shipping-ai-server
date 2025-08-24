import os, argparse
import numpy as np
from collections import defaultdict
import joblib

# 패키지 기준 import (중요!)
from app.service.datato import load_ei_rows_from_csv
from app.service.train_xgb import EIBaseline, train_ei_residual, predict_from_ei
from app.service.sea import SeaMap, PortDB, SeaRouter

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

# ---------------------------
# 3) 베이스라인 설정
# ---------------------------
def make_baseline():
    return EIBaseline(
        ef_ton_per_ton=3.114,   # HFO 예시
        reserve_ratio=0.05,
        sfoc_g_per_kwh=180.0,   # 예시 값
        speed_kn=18.0,          # 예시 값
        alpha=1.0,
        teu_ref=8000.0
    )

# ---------------------------
# 4) 학습
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
# 6) 저장/로드
# ---------------------------
def save_model(pack, path="models/ei_residual.joblib"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(pack, path)
    print(f"[INFO] Saved model to {path}")

def load_model(path="models/ei_residual.joblib"):
    return joblib.load(path)

# ---------------------------
# main
# ---------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/train.csv")
    ap.add_argument("--encoding", default="utf-8-sig")
    ap.add_argument("--save", default="models/ei_residual.joblib")
    ap.add_argument("--predict-origin", default=None)
    ap.add_argument("--predict-dest", default=None)
    ap.add_argument("--teu", type=float, default=8000.0)

    # ⇩ 새로 추가
    ap.add_argument("--port-db", default=os.getenv("PORT_DB", "Port_DB.csv"))
    ap.add_argument("--land", default=os.getenv("LAND_PATH", "land.geojson"))
    ap.add_argument("--nogo", default=os.getenv("NOGO_PATH", "") or None)
    ap.add_argument("--coast-buffer-km", type=float, default=0.0)
    ap.add_argument("--corridor-buffer-km", type=float, default=800.0)
    ap.add_argument("--step-deg", type=float, default=0.5)
    ap.add_argument("--max-edge-km", type=float, default=150.0)
    ap.add_argument("--terminal-k", type=int, default=24)

    args = ap.parse_args()

    rows = load_rows(args.csv, encoding=args.encoding)

    # 기존: dp = make_distance_provider_from_csv(rows)
    # 교체: 해상 경로 provider 사용
    dp = make_distance_provider_from_sea(
        port_db_csv=args.port_db,
        land_path=args.land,
        nogo_path=args.nogo,
        coast_buffer_km=args.coast_buffer_km,
        corridor_buffer_km=args.corridor_buffer_km,
        step_deg=args.step_deg,
        connect_8=True,
        max_edge_km=args.max_edge_km,
        terminal_k=args.terminal_k,
    )

    pack = train_model(rows)
    save_model(pack, args.save)
    pack2 = load_model(args.save)

    origin = args.predict_origin or rows[0].origin
    dest   = args.predict_dest or rows[0].dest
    sample_predict(pack2, dp, origin, dest, teu_loaded=args.teu)


if __name__ == "__main__":
    main()
