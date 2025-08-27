# app/service/deps.py
from __future__ import annotations
import os
from functools import lru_cache
import joblib

from app.models.geo.geo_models.DistanceProvider import make_distance_provider_from_route

@lru_cache(maxsize=1)
def get_distance_provider():
    port_csv = os.getenv("PORT_DB", "data/Port_DB_utf8.csv")
    port_enc = os.getenv("PORT_DB_ENCODING") or None
    grid_km  = float(os.getenv("GRID_KM", 60.0))
    coast_km = float(os.getenv("COAST_KM", 12.0))
    return make_distance_provider_from_route(
        port_csv=port_csv,
        grid_spacing_km=grid_km,
        coast_buffer_km=coast_km,
        port_encoding=port_enc,
    )

@lru_cache(maxsize=1)
def get_model_pack():
    path = os.getenv("EI_MODEL_PATH", "app/models/model_store/ei_residual.joblib")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"모델 파일이 없습니다: {path} — 먼저 학습해 .joblib을 생성하세요."
        )
    return joblib.load(path)  # TrainedEIResidual
