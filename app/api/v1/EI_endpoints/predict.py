# app/api/v1/endpoints/predict.py
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional

from app.service.deps import get_distance_provider, get_model_pack
from app.service.feature import EIPayload, prepare_inputs
from app.service.train_xgb import predict_from_ei
from app.service.data_set import EF as EF_TABLE  # 연료 EF 테이블

router = APIRouter()  # ← 여기선 prefix를 두지 않고, include 할 때 붙일 거야.

class EIPredictRequest(BaseModel):
    origin: str = Field(..., description="출발항")
    dest: str = Field(..., description="도착항")
    teu_loaded: float = Field(..., gt=0, description="적재량(TEU)")
    fuel: str = Field(..., description="연료종류(HFO/LFO/MDO/MGO/LNG)")

    # (옵션) 확장용
    speed_knots: Optional[float] = Field(None, ge=0)
    sfoc_g_per_kwh: Optional[float] = Field(None, ge=0)
    k: Optional[float] = Field(None, ge=0)

    @validator("fuel")
    def _fuel_norm(cls, v: str) -> str:
        fu = v.strip().upper()
        if fu not in EF_TABLE:
            raise ValueError(f"지원하지 않는 연료: {v} (허용: {', '.join(EF_TABLE.keys())})")
        return fu

class EIPredictResponse(BaseModel):
    origin: str
    dest: str
    fuel: str
    route_distance_nm: float
    route_distance_km: float
    ei_kg_per_teu_km: float
    co2_ton: float
    fc_ton: float

@router.post("/ei", response_model=EIPredictResponse)
def predict_ei(
    body: EIPredictRequest,
    distance_provider = Depends(get_distance_provider),
    model_pack = Depends(get_model_pack),
):
    try:
        payload = EIPayload(
            origin=body.origin, dest=body.dest,
            teu_loaded=body.teu_loaded, fuel=body.fuel,
            speed_knots=body.speed_knots,
            sfoc_g_per_kwh=body.sfoc_g_per_kwh,
            k=body.k,
        )
        prep = prepare_inputs(payload, distance_provider)

        out = predict_from_ei(
            pack=model_pack,
            origin=prep["origin"],
            dest=prep["dest"],
            teu_loaded=prep["teu_loaded"],
            distance_provider=distance_provider,
        )
        reserve_ratio = model_pack.baseline.reserve_ratio
        ef_user = EF_TABLE[prep["fuel"]]
        denom = ef_user * (1 - reserve_ratio)
        if denom <= 0:
            raise ValueError("EF*(1-r) <= 0")
        fc_ton_user = out["co2_ton"] / denom

        return EIPredictResponse(
            origin=prep["origin"],
            dest=prep["dest"],
            fuel=prep["fuel"],
            route_distance_nm=prep["distance_nm"],
            route_distance_km=out["distance_km"],
            ei_kg_per_teu_km=out["ei_kg_per_teu_km"],
            co2_ton=out["co2_ton"],
            fc_ton=fc_ton_user,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
