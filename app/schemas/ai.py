from __future__ import annotations

from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="사용자 질문")
    distance_nm: Optional[float] = None
    base_speed_knots: Optional[float] = None
    new_speed_knots: Optional[float] = None
    sfoc_g_per_kwh: Optional[float] = None
    k: Optional[float] = None
    vessel_type: Optional[str] = None
    language: str = Field(default="ko", description="응답 언어(예: ko, en, ja)")


class Metrics(BaseModel):
    fc_base_ton: Optional[float] = None
    fc_new_ton: Optional[float] = None
    co2_base_ton: Optional[float] = None
    co2_new_ton: Optional[float] = None
    co2_reduction_pct: Optional[float] = None
    time_base_hours: Optional[float] = None
    time_new_hours: Optional[float] = None
    time_delta_hours: Optional[float] = None
    time_increase_pct: Optional[float] = None
    assumptions: Optional[List[str]] = None
    notes: Optional[str] = None


class Citation(BaseModel):
    source: Optional[str] = None
    path: Optional[str] = None
    snippet: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    metrics: Optional[Metrics] = None
    assumptions: Optional[List[str]] = None
    citations: List[Citation] = []


class Scenario(BaseModel):
    distance_nm: float
    base_speed_knots: float
    new_speed_knots: float
    sfoc_g_per_kwh: Optional[float] = None
    k: Optional[float] = None
    vessel_type: Optional[str] = None


class ReportRequest(BaseModel):
    scenarios: List[Scenario]
    title: str = "ESG Report"
    language: str = Field(default="ko")


class ReportResponse(BaseModel):
    report_path: str
    summary: Optional[str] = None

