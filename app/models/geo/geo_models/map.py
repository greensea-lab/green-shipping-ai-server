# .venv/Scripts/python app/models/geo/geo_models/map.py
import os, json, sys, glob, subprocess
import folium
from folium.plugins import MiniMap, Fullscreen, MousePosition, MeasureControl
import geopandas as gpd

HERE      = os.path.abspath(os.path.dirname(__file__))                  # .../app/models/geo/geo_models
ROOT_GEO  = os.path.abspath(os.path.join(HERE, ".."))                   # .../app/models/geo
ROOT      = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..")) # 프로젝트 루트
OUT_DIR   = os.path.join(ROOT_GEO, "output")                            # .../app/models/geo/output

ROUTE_PATH = os.path.join(OUT_DIR, "route.geojson")
OD_PATH    = os.path.join(OUT_DIR, "od_ports.geojson")
ROUTE_SCRIPT = os.path.join(HERE, "route.py")                           # 같은 폴더의 route.py 가정


# 프로젝트 전역 map*.html 정리(항상 최신 한 개만 유지) => 보수 필요
def cleanup_old_htmls():
    patterns = [
        os.path.join(ROOT, "map*.html"),
        os.path.join(ROOT, "app", "**", "map*.html"),
    ]
    removed = 0
    for pat in patterns:
        for p in glob.glob(pat, recursive=True):
            try:
                os.remove(p); removed += 1
            except OSError:
                pass
    if removed:
        print(f"🧹 Removed {removed} old HTML file(s)")

def ensure_geojson():
    """route/od 파일이 없으면 route.py를 자동 실행해서 생성 시도."""
    if os.path.exists(ROUTE_PATH) and os.path.exists(OD_PATH):
        return True
    print("ℹ️ GeoJSON이 없어 route.py를 실행합니다…")
    try:
        # 현재 파이썬으로 route.py 실행 (가상환경에서 실행 중이면 그대로 상속)
        subprocess.run([sys.executable, ROUTE_SCRIPT], check=True)
    except Exception as e:
        print(f"❌ route.py 실행 실패: {e}")
        return False
    ok = os.path.exists(ROUTE_PATH) and os.path.exists(OD_PATH)
    if not ok:
        print("❌ route.py 실행 후에도 GeoJSON이 없습니다.")
    return ok

def load_nonempty_gdf(path: str):
    #GeoJSON 로드 후 빈/Null geometry 제거.
    gdf = gpd.read_file(path)
    if gdf is None:
        return None
    if "geometry" not in gdf.columns:
        return None
    gdf = gdf[ gdf.geometry.notnull() & ~gdf.geometry.is_empty ]
    return gdf if len(gdf) else None

def compute_center_and_bounds(route_gdf, od_gdf):
    #경로가 있으면 경로 centroid/bounds, 없으면 OD 기준.
    if route_gdf is not None and len(route_gdf):
        r4326 = route_gdf.to_crs("EPSG:4326")
        union = r4326.unary_union
        center = union.centroid
        minx, miny, maxx, maxy = r4326.total_bounds
    else:
        o4326 = od_gdf.to_crs("EPSG:4326")
        union = o4326.unary_union
        center = union.centroid
        minx, miny, maxx, maxy = o4326.total_bounds
    return center, (minx, miny, maxx, maxy)

def main():
    # 0) GeoJSON 확보
    if not ensure_geojson():
        print("❌ GeoJSON을 찾을 수 없습니다. 수동으로 route.py를 먼저 실행하세요.")
        print("   찾는 경로:", OUT_DIR)
        sys.exit(1)

    # 1) 기존 HTML 정리
    cleanup_old_htmls()

    # 2) 데이터 로드(빈/Null geometry 제거)
    route = load_nonempty_gdf(ROUTE_PATH)
    od    = load_nonempty_gdf(OD_PATH)

    if od is None or len(od) == 0:
        print(f"❌ OD 포인트가 비어 있습니다: {OD_PATH}")
        sys.exit(1)

    # 3) 중심/범위 계산 (route 없으면 OD로 폴백)
    center, bounds = compute_center_and_bounds(route, od)

    # 4) 지도 생성
    m = folium.Map(location=[center.y, center.x], zoom_start=4,
                   tiles="OpenStreetMap", control_scale=True)

    # 5) 경로 레이어(있을 때만)
    if route is not None and len(route):
        folium.GeoJson(
            json.loads(route.to_json()),
            name="Sea Route (A*)",
            style_function=lambda f: {"color": "#ff6b00", "weight": 5, "opacity": 0.95},
        ).add_to(m)
    else:
        print("⚠ route.geojson이 비어 있어 OD만 표시합니다.")

    # 6) O/D 포인트
    for _, r in od.iterrows():
        lat, lon = r.geometry.y, r.geometry.x
        folium.CircleMarker(
            location=(lat, lon),
            radius=6,
            color="#1f77b4",
            fill=True,
            fill_opacity=0.95,
            tooltip=r.get("name", "Port"),
        ).add_to(m)

    # 7) 편의 기능
    MiniMap(toggle_display=True).add_to(m)
    Fullscreen().add_to(m)
    MousePosition(position="bottomleft", separator=" | ", prefix="Lat/Lon:").add_to(m)
    m.add_child(MeasureControl(primary_length_unit="nautical_miles"))
    folium.LayerControl(collapsed=False).add_to(m)

    # 8) 보기 범위 맞춤
    minx, miny, maxx, maxy = bounds
    try:
        m.fit_bounds([[miny, minx], [maxy, maxx]], padding=(20, 20))
    except Exception:
        pass

    # 9) 저장
    out_html = os.path.join(ROOT, "map.html")  # 항상 루트에 저장
    m.save(out_html)
    print(f"✅ Saved map to {out_html}")

if __name__ == "__main__":
    main()

