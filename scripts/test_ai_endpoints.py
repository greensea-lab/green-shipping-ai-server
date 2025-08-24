import os
import sys
from pathlib import Path

# Ensure stubs are imported before heavy libs
ROOT = Path(__file__).resolve().parents[1]
STUBS = ROOT / "stubs"
sys.path.insert(0, str(STUBS))

# Force lightweight local DB to avoid hanging on MySQL during tests
os.environ["DATABASE_URL"] = os.environ.get("DATABASE_URL", f"sqlite:///{ROOT/'local.db'}")

import asyncio
import httpx

# Minimal env setup
os.environ.setdefault("INTERNAL_API_TOKEN", "test-internal-token")
os.environ.setdefault("OPENAI_API_KEY", "sk-test")
os.environ.setdefault("AI_MODEL", "gpt-4o-mini")
os.environ.setdefault("EMBEDDING_MODEL", "text-embedding-3-small")
os.environ.setdefault("RAG_PERSIST_DIR", str(ROOT / "data" / "chroma-test"))

from app.main import app  # after env & stubs on sys.path


async def run_async():
    headers = {"x-internal-token": os.environ["INTERNAL_API_TOKEN"]}
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1) chat (simulation only; no KB used)
        chat_body = {"message": "테스트 질문입니다.", "language": "ko", "distance_nm": 100, "base_speed_knots": 12, "new_speed_knots": 10}
        r = await client.post("/api/v1/ai/chat", json=chat_body, headers=headers)
        print("chat:", r.status_code, r.json().get("answer", ""))

        # 2) KB ingest + search using stub chroma
        kb_dir = ROOT / "kb"
        kb_dir.mkdir(parents=True, exist_ok=True)
        sample = kb_dir / "sample.txt"
        sample.write_text("이것은 테스트 문서입니다. 친환경 해운과 탄소 배출에 관한 내용.", encoding="utf-8")
        r = await client.post("/api/v1/ai/kb/ingest", json=[str(sample)], headers=headers)
        print("kb.ingest:", r.status_code, r.json())
        r = await client.get("/api/v1/ai/kb/search", params={"query": "탄소 배출"}, headers=headers)
        print("kb.search:", r.status_code, r.json())

        # 3) report
        body = {
            "title": "테스트 보고서",
            "language": "ko",
            "scenarios": [
                {"distance_nm": 100, "base_speed_knots": 12, "new_speed_knots": 10},
                {"distance_nm": 200, "base_speed_knots": 14, "new_speed_knots": 12}
            ]
        }
        r = await client.post("/api/v1/ai/report", json=body, headers=headers)
        print("report:", r.status_code, r.json())


if __name__ == "__main__":
    asyncio.run(run_async())
