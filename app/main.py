from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.api import api_router
from app.database import engine, Base

# Create database tables (only if database is available)
try:
    Base.metadata.create_all(bind=engine)
    print("✅ 데이터베이스 테이블이 생성되었습니다.")
except Exception as e:
    print(f"⚠️  데이터베이스 연결 실패: {e}")
    print("📋 API는 더미 데이터로 작동합니다.")

# Create FastAPI app
app = FastAPI(
    title="Green Shipping AI Server",
    description="FastAPI backend server for Green Shipping AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Green Shipping AI Server"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 