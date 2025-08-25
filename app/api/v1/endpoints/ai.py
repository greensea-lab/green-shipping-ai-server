from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Header, status

from app.config import settings
from app.ai.llm import get_chat_model
from app.ai.sim_adapter import SimAdapter, SpeedChangeInput
from app.ai.kb import ingest_kb, search_kb
from app.ai.prompts import SYSTEM_PROMPT, build_user_prompt
from app.ai.report import generate_esg_report_pdf
from app.schemas.ai import (
    ChatRequest, ChatResponse, Metrics, Citation,
    ReportRequest, ReportResponse
)


router = APIRouter()


def require_internal_token(x_internal_token: Optional[str] = Header(None)):
    token = settings.internal_api_token
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Internal API token not configured")
    if x_internal_token != token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return True


@router.post("/chat", response_model=ChatResponse, summary="생성형 AI 질의응답(내부 전용)")
def ai_chat(req: ChatRequest, _: bool = Depends(require_internal_token)):
    # Optional simulation
    metrics_obj: Optional[Metrics] = None
    assumptions: List[str] = []
    if req.distance_nm and req.base_speed_knots and req.new_speed_knots:
        sim = SimAdapter()
        res = sim.simulate_speed_change(
            SpeedChangeInput(
                distance_nm=req.distance_nm,
                base_speed_knots=req.base_speed_knots,
                new_speed_knots=req.new_speed_knots,
                sfoc_g_per_kwh=req.sfoc_g_per_kwh,
                k=req.k,
                vessel_type=req.vessel_type,
            )
        )
        metrics_obj = Metrics(**res.__dict__)
        assumptions = res.assumptions or []

    # KB lookup (may return empty list if nothing ingested)
    citations_raw = search_kb(req.message, top_k=3)
    citations = [Citation(**c) for c in citations_raw]

    # Build prompt and call model
    answer_text: str
    if not settings.openai_api_key:
        # Fallback answer without LLM when API key is not set
        parts = []
        lang = (req.language or "ko").lower()
        if lang.startswith("ko"):
            parts.append("[주의] LLM 키가 설정되지 않아 기본 응답을 제공합니다.")
            parts.append(f"질문: {req.message}")
            if metrics_obj:
                m = metrics_obj
                parts.append("요약: 속도 변경에 따른 주요 지표는 다음과 같습니다.")
                parts.append(f"- CO2: {m.co2_base_ton} → {m.co2_new_ton} (감소율 {m.co2_reduction_pct}%)")
                parts.append(f"- 시간: {m.time_base_hours}h → {m.time_new_hours}h (Δ {m.time_delta_hours}h, {m.time_increase_pct}%)")
                parts.append("해당 수치는 내부 시뮬레이터(스텁) 결과를 기반으로 산출되었습니다.")
            else:
                parts.append("계산 파라미터가 부족하여 수치 요약은 제공되지 않습니다.")
            if citations:
                parts.append("참고 문서:")
                for c in citations:
                    parts.append(f"- {c.source} ({c.path})")
            answer_text = "\n".join(parts)
        else:
            # Simple English default
            parts.append("[Note] LLM key not configured; returning a basic response.")
            parts.append(f"Question: {req.message}")
            if metrics_obj:
                m = metrics_obj
                parts.append("Summary: key metrics for the speed change:")
                parts.append(f"- CO2: {m.co2_base_ton} → {m.co2_new_ton} (reduction {m.co2_reduction_pct}%)")
                parts.append(f"- Time: {m.time_base_hours}h → {m.time_new_hours}h (Δ {m.time_delta_hours}h, {m.time_increase_pct}%)")
                parts.append("Figures are from the internal simulator (stub).")
            else:
                parts.append("Insufficient parameters for numeric summary.")
            if citations:
                parts.append("References:")
                for c in citations:
                    parts.append(f"- {c.source} ({c.path})")
            answer_text = "\n".join(parts)
    else:
        llm = get_chat_model()
        metrics_dict = metrics_obj.dict() if metrics_obj else None
        user_prompt = build_user_prompt(req.language, req.message, metrics_dict, citations_raw)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        out = llm.invoke(messages)
        # Ensure answer_text is always a string
        if hasattr(out, "content"):
            content = out.content
            if isinstance(content, str):
                answer_text = content
            elif isinstance(content, list):
                # Convert list to string representation
                answer_text = str(content)
            else:
                answer_text = str(content)
        else:
            answer_text = str(out)

    return ChatResponse(
        answer=answer_text,
        metrics=metrics_obj,
        assumptions=assumptions,
        citations=citations,
    )


@router.post("/report", response_model=ReportResponse, summary="ESG 보고서 PDF 생성(내부 전용)")
def ai_report(req: ReportRequest, _: bool = Depends(require_internal_token)):
    # Run simulation per scenario
    sim = SimAdapter()
    results = []
    for s in req.scenarios:
        res = sim.simulate_speed_change(
            SpeedChangeInput(
                distance_nm=s.distance_nm,
                base_speed_knots=s.base_speed_knots,
                new_speed_knots=s.new_speed_knots,
                sfoc_g_per_kwh=s.sfoc_g_per_kwh,
                k=s.k,
                vessel_type=s.vessel_type,
            )
        )
        results.append(res.__dict__)

    path = generate_esg_report_pdf(
        scenarios=[s.dict() for s in req.scenarios],
        results=results,
        title=req.title,
        language=req.language,
    )

    # Short summary via LLM
    if not settings.openai_api_key:
        # Simple summary without LLM
        summary = (
            f"보고서 '{req.title}' 요약: 총 {len(req.scenarios)}개 시나리오에 대해 CO₂ 감축과 운항시간 변화를 산출했습니다. "
            f"상세 수치는 본문 표를 참고하세요. (LLM 요약 비활성화)"
        ) if (req.language or "ko").lower().startswith("ko") else (
            f"Summary for '{req.title}': computed CO₂ reductions and time deltas across {len(req.scenarios)} scenarios. "
            f"See the tables for details. (LLM summary disabled)"
        )
    else:
        llm = get_chat_model()
        summary_prompt = (
            f"Language: {req.language}\n"
            f"Create a 2-3 sentence executive summary of the ESG report titled '{req.title}'.\n"
            f"Focus on CO2 reduction and time impact across {len(req.scenarios)} scenarios."
        )
        llm_result = llm.invoke([{ "role": "system", "content": "You summarize reports succinctly."},
                                 { "role": "user", "content": summary_prompt }])
        
        # Ensure summary is always a string
        if hasattr(llm_result, "content"):
            content = llm_result.content
            if isinstance(content, str):
                summary = content
            else:
                summary = str(content)
        else:
            summary = str(llm_result)

    return ReportResponse(report_path=path, summary=summary)


@router.post("/kb/ingest", summary="KB 인제스트(내부 전용)")
def kb_ingest(paths: Optional[List[str]] = None, _: bool = Depends(require_internal_token)):
    n = ingest_kb(paths)
    return {"added_chunks": n}


@router.get("/kb/search", summary="KB 검색(내부 전용)")
def kb_search(query: str, top_k: int = 3, _: bool = Depends(require_internal_token)):
    return {"hits": search_kb(query, top_k=top_k)}
