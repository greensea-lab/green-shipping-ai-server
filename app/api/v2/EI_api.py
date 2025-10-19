# EI_api.py
from fastapi import FastAPI
from app.api.v2.EI_endpoints.predict import router as predict_router

app = FastAPI(
    title="EI Prediction API",
    version="1.0.0",
    description="선박 항로 기반 탄소배출량/EI 예측 API"
)

# 기본 헬스체크
@app.get("/health")
def health():
    return {"status": "ok"}

# predict 라우터 연결
app.include_router(predict_router, prefix="/api/v2")