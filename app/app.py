# python -m uvicorn app.app:app --reload
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal
from app.models.port_queries import search_ports
from app.models.geo.geo_models import route
from pyproj import Geod  # 총거리 계산용


app = FastAPI(title="GreenShipping API")

# CORS (프론트 개발 중엔 * 허용, 운영에선 특정 도메인만)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # TODO: prod에서 바꾸기
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"ok": True, "service": "GreenShipping API"}

@app.get("/health")
def health():
    return {"status": "healthy"}


# -------------------------------
# 1) 자동완성 API
# -------------------------------
@app.get("/ports")
def autocomplete_ports(
    q: str = Query(..., min_length=1, description="검색어(영문/한글 일부)"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    항만 자동완성 API
    - GET /ports?q=busan&limit=10
    - 응답: [{ id, name, kr, country, iso2, lat, lon }, ...]
    """
    db = SessionLocal()
    try:
        rows = search_ports(db, q, limit)
        return [
            {
                "id": p.id,
                "name": p.english_name,
                "kr": p.korean_name,
                "country": p.country_eng,
                "iso2": p.country_code,
                "lat": p.latitude,
                "lon": p.longitude,
            }
            for p in rows
        ]
    finally:
        db.close()


# -------------------------------
# 2) 경로 계산 API
# -------------------------------
@app.get("/route")
def compute_route(origin: str, dest: str):
    """
    O/D 포트명을 받아 경로 계산 → 요약 + GeoJSON 반환
    - summary: 총거리(km), O/D 좌표
    - geojson: LineString FeatureCollection (지도 라이브러리에 바로 올리기 가능)
    """
    try:
        # route.py 전역 설정 (DB모드 강제)
        route.USE_DB = True
        route.ORIGIN_NAME = origin
        route.DEST_NAME = dest

        # 경로 계산 (결과 파일 생성: route.ROUTE_PATH, route.OD_PATH)
        route.run_pipeline()

        # GeoJSON 읽기
        import json
        with open(route.ROUTE_PATH, encoding="utf-8") as f:
            gj = json.load(f)

        # 경로 좌표 (첫/마지막 점을 O/D로 사용)
        features = gj.get("features", [])
        if not features:
            raise RuntimeError("empty geojson")
        coords = features[0]["geometry"]["coordinates"]  # [[lon,lat], ...]
        o_lon, o_lat = coords[0]
        d_lon, d_lat = coords[-1]

        # 총거리 계산(WGS84)
        g = Geod(ellps="WGS84")
        dist_m = 0.0
        for (x1, y1), (x2, y2) in zip(coords, coords[1:]):
            _, _, d = g.inv(x1, y1, x2, y2)  # meters
            dist_m += d

        return {
            "summary": {
                "origin": {"name": origin, "lon": o_lon, "lat": o_lat},
                "dest":   {"name": dest,   "lon": d_lon, "lat": d_lat},
                "distance_km": round(dist_m / 1000.0, 1),
            },
            "geojson": gj,
        }

    except ValueError as e:
        # 예: 포트명이 DB에 없음
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # 기타 오류
        raise HTTPException(status_code=500, detail=f"route failed: {e}")
