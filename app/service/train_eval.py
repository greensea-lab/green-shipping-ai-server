# app/service/train_eval.py
import os, argparse
import joblib

from app.service.datato import load_ei_rows_from_csv
from app.service.train_xgb import (
    EIBaseline,
    train_ei_residual,
    predict_from_ei,
)
from app.models.geo.geo_models.DistanceProvider import (
    make_distance_provider_from_route,
)

def load_rows(csv_path: str, encoding: str = "utf-8-sig"):
    rows = load_ei_rows_from_csv(csv_path, encoding=encoding)
    if not rows:
        raise RuntimeError("학습 데이터가 비어있습니다.")
    print(f"[INFO] Loaded {len(rows)} rows from {csv_path}")
    return rows

def make_baseline():
    return EIBaseline(
        ef_ton_per_ton=3.114,
        reserve_ratio=0.05,
        sfoc_g_per_kwh=180.0,
        speed_kn=18.0,
        alpha=1.0,
        teu_ref=8000.0,
    )

def train_model(rows):
    baseline = make_baseline()
    return train_ei_residual(rows, baseline, fuel_name="HFO")

def sample_predict(pack, dp, origin, dest, teu_loaded=8000):
    pred = predict_from_ei(
        pack=pack,
        origin=origin,
        dest=dest,
        teu_loaded=float(teu_loaded),
        distance_provider=dp,
    )
    print(f"[PRED] {origin} -> {dest}")
    for k, v in pred.items():
        print(f"  {k}: {v}")
    return pred

def save_model(pack, path="models/ei_residual.joblib"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(pack, path)
    print(f"[INFO] Saved model to {path}")

def load_model(path="models/ei_residual.joblib"):
    return joblib.load(path)

def main():
    ap = argparse.ArgumentParser()

    # 데이터/저장
    ap.add_argument("--csv", default="data/train.csv")
    ap.add_argument("--encoding", default="utf-8-sig")
    ap.add_argument("--save", default="models/ei_residual.joblib")

    # 예측 샘플
    ap.add_argument("--predict-origin", default=None)
    ap.add_argument("--predict-dest", default=None)
    ap.add_argument("--teu", type=float, default=8000.0)

    # DistanceProvider 파라미터
    ap.add_argument("--port-db", default=os.getenv("PORT_DB", "data/Port_DB.csv"))
    ap.add_argument("--port-db-encoding", default=None)          # ✅ 추가
    ap.add_argument("--grid-km", type=float, default=60.0)
    ap.add_argument("--coast-km", type=float, default=12.0)

    args = ap.parse_args()

    rows = load_rows(args.csv, encoding=args.encoding)

    dp = make_distance_provider_from_route(
        port_csv=args.port_db,
        grid_spacing_km=args.grid_km,
        coast_buffer_km=args.coast_km,
        port_encoding=args.port_db_encoding,        # ✅ 전달
    )

    pack = train_model(rows)
    save_model(pack, args.save)
    pack2 = load_model(args.save)

    origin = args.predict_origin or rows[0].origin
    dest   = args.predict_dest or rows[0].dest
    sample_predict(pack2, dp, origin, dest, teu_loaded=args.teu)

if __name__ == "__main__":
    main()
