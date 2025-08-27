# app/api/predict.py
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional

from app.service.deps import get_distance_provider, get_model_pack
from app.service.feature import EIPayload, prepare_inputs
from app.service.train_xgb import predict_from_ei          # ← 네 현재 경로 유지
from app.service.data_set import EF as EF_TABLE            # 연료 EF 테이블(HFO/LFO/MGO/LNG 등)

router = APIRouter(prefix="/predict", tags=["predict"])

# ---------- 요청/응답 스키마 ----------
class EIPredictRequest(BaseModel):
    origin: str = Field(..., description="출발항 이름/코드")
    dest: str = Field(..., description="도착항 이름/코드")
    teu_loaded: float = Field(..., gt=0, description="적재량(TEU)")
    fuel: str = Field(..., description="연료종류 (HFO/LFO/MDO/MGO/LNG 등)")

    # (옵션) 추후 baseline/로그 확장용
    speed_knots: Optional[float] = Field(None, ge=0)
    sfoc_g_per_kwh: Optional[float] = Field(None, ge=0)
    k: Optional[float] = Field(None, ge=0)

    @validator("fuel")
    def _fuel_norm(cls, v: str) -> str:
        s = v.strip().upper()
        if s not in EF_TABLE:
            allowed = ", ".join(EF_TABLE.keys())
            raise ValueError(f"지원하지 않는 연료입니다: {v} (허용: {allowed})")
        return s

class EIPredictResponse(BaseModel):
    origin: str
    dest: str
    fuel: str
    route_distance_nm: float
    route_distance_km: float
    ei_kg_per_teu_km: float
    co2_ton: float
    fc_ton: float

# ---------- 엔드포인트 ----------
@router.post("/ei", response_model=EIPredictResponse)
def predict_ei_api(
    body: EIPredictRequest,
    distance_provider = Depends(get_distance_provider),
    model_pack = Depends(get_model_pack),
):
    """
    흐름:
    1) 입력 검증/정규화 + 거리 계산(feature.prepare_inputs)
    2) EI/CO2는 잔차모델(predict_from_ei)로 산출
    3) FC는 사용자 '연료종류'의 EF로 재계산 (CO2는 연료 무관)
    """
    try:
        # 1) 입력 전처리(거리 nm/km, EF 확인)
        payload = EIPayload(
            origin=body.origin, dest=body.dest,
            teu_loaded=body.teu_loaded, fuel=body.fuel,
            speed_knots=body.speed_knots,
            sfoc_g_per_kwh=body.sfoc_g_per_kwh,
            k=body.k,
        )
        prep = prepare_inputs(payload, distance_provider)

        # 2) EI/CO2/FC(기본 EF) — EI/CO2는 연료 무관
        out = predict_from_ei(
            pack=model_pack,
            origin=prep["origin"],
            dest=prep["dest"],
            teu_loaded=prep["teu_loaded"],
            distance_provider=distance_provider,
        )
        # out: {"distance_km","ei_kg_per_teu_km","co2_ton","fc_ton"}

        # 3) 연료 반영 FC 재계산 (CO2는 그대로)
        reserve_ratio = model_pack.baseline.reserve_ratio
        ef_user = EF_TABLE[prep["fuel"]]                          # ton CO2 / ton fuel
        denom = ef_user * (1.0 - reserve_ratio)
        if denom <= 0:
            raise ValueError("EF*(1-r) <= 0 (연료/예비율 설정 확인)")
        fc_ton_user = out["co2_ton"] / denom

        return EIPredictResponse(
            origin=prep["origin"],
            dest=prep["dest"],
            fuel=prep["fuel"],
            route_distance_nm=prep["distance_nm"],     # provider로 계산한 값
            route_distance_km=out["distance_km"],      # predict_from_ei 내부도 동일 거리 사용
            ei_kg_per_teu_km=out["ei_kg_per_teu_km"],
            co2_ton=out["co2_ton"],
            fc_ton=fc_ton_user,                        # ⬅️ 사용자 연료 EF 반영한 FC
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
