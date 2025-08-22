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
    llm = get_chat_model()
    metrics_dict = metrics_obj.dict() if metrics_obj else None
    user_prompt = build_user_prompt(req.language, req.message, metrics_dict, citations_raw)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    out = llm.invoke(messages)
    answer_text = out.content if hasattr(out, "content") else str(out)

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
    llm = get_chat_model()
    summary_prompt = (
        f"Language: {req.language}\n"
        f"Create a 2-3 sentence executive summary of the ESG report titled '{req.title}'.\n"
        f"Focus on CO2 reduction and time impact across {len(req.scenarios)} scenarios."
    )
    summary = llm.invoke([{ "role": "system", "content": "You summarize reports succinctly."},
                          { "role": "user", "content": summary_prompt }]).content

    return ReportResponse(report_path=path, summary=summary)


@router.post("/kb/ingest", summary="KB 인제스트(내부 전용)")
def kb_ingest(paths: Optional[List[str]] = None, _: bool = Depends(require_internal_token)):
    n = ingest_kb(paths)
    return {"added_chunks": n}


@router.get("/kb/search", summary="KB 검색(내부 전용)")
def kb_search(query: str, top_k: int = 3, _: bool = Depends(require_internal_token)):
    return {"hits": search_kb(query, top_k=top_k)}

