# GreenShipping 최단거리 초기모델 🚢

Windows (Git Bash) 환경에서 **GeoPandas / Folium 기반 해상 경로**를 실행하는 방법입니다.  
최단거리 A* 알고리즘 기반으로 경로를 계산하고, Folium HTML 지도로 시각화합니다.

---

```bash
1) 환경 준비

1-1. 가상환경 생성 및 활성화
/c/Users/<본인계정>/AppData/Local/Programs/Python/Python311/python.exe -m venv .venv
source .venv/Scripts/activate

1-2. 필수 패키지 설치
python -m pip install --upgrade pip setuptools wheel
pip install "geopandas>=1.0,<2.0" shapely>=2.0 pyproj>=3.6 fiona>=1.9 matplotlib rtree mapclassify folium geodatasets

1-3. 설치 확인 (버전 출력)
python - << 'PY'
import geopandas as gpd, shapely, pyproj, fiona
print("GeoPandas:", gpd.__version__)
print("Shapely:", shapely.__version__)
print("PyProj:", pyproj.__version__)
print("Fiona:", fiona.__version__)
PY

2) 실행 방법

2-1. 경로 계산 (A* 기반)
**CSV로 실행 시**
.venv/Scripts/python app/models/geo/geo_models/route.py
**db 조회로 실행 시**
python -m app.models.check_port
USE_DB=1 python -m app.models.geo.geo_models.route -o "출발지명" -d "도착지명"

➡ 콘솔에 경로 거리 (km) 가 출력됩니다.
➡ 결과 파일:
app/models/geo/output/route.geojson
app/models/geo/output/od_ports.geojson

2-2. 지도 생성 (Folium)
.venv/Scripts/python app/models/geo/geo_models/map.py
➡ 프로젝트 루트에 map.html 생성
➡ 실행 시 기존 map*.html 파일은 자동 정리되고 최신 파일만 유지됩니다.

2-3. 브라우저에서 지도 열기
start map.html
