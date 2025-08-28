#!/usr/bin/env python
"""
Ad-hoc tester for LLM API endpoints using FastAPI TestClient.

Runs two calls:
  1) Chat with speed-change inputs (stub path)
  2) Chat with EI route-based inputs (graceful degrade offline)

This test forces OPENAI off to avoid network calls.
"""
import os, sys
from pprint import pprint

# Force LLM and embeddings to offline behavior
os.environ["OPENAI_API_KEY"] = ""

# Add project root to PYTHONPATH
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.config import settings
settings.openai_api_key = None  # ensure fallback in endpoints

from app.api.v1.endpoints.ai import ai_chat, ai_report
from app.schemas.ai import ChatRequest, ReportRequest, Scenario


def run():
    print("\n== Chat: speed-change only ==")
    payload1 = {
        "message": "속력 15kn에서 12kn으로 낮추면 연료와 CO2, 시간 영향은?",
        "distance_nm": 1000,
        "base_speed_knots": 15,
        "new_speed_knots": 12,
        "language": "ko",
    }
    r1 = ai_chat(ChatRequest(**payload1), True)
    pprint(r1.model_dump() if hasattr(r1, 'model_dump') else r1.dict())

    print("\n== Chat: route-based EI inputs (offline-friendly) ==")
    payload2 = {
        "message": "부산에서 로스앤젤레스로 8000TEU HFO 기준 EI/CO2 예측해줘",
        "origin": "BUSAN",
        "dest": "LOS ANGELES",
        "teu_loaded": 8000,
        "fuel": "HFO",
        "language": "ko",
    }
    r2 = ai_chat(ChatRequest(**payload2), True)
    pprint(r2.model_dump() if hasattr(r2, 'model_dump') else r2.dict())

    print("\n== Report: one scenario with speed-change + route fields ==")
    req = ReportRequest(
        title="테스트 리포트",
        language="ko",
        scenarios=[
            Scenario(
                distance_nm=1200,
                base_speed_knots=15,
                new_speed_knots=12,
                origin="BUSAN",
                dest="LOS ANGELES",
                teu_loaded=8000,
                fuel="HFO",
            )
        ],
    )
    rep = ai_report(req, True)
    pprint(rep.model_dump() if hasattr(rep, 'model_dump') else rep.dict())


if __name__ == "__main__":
    run()
