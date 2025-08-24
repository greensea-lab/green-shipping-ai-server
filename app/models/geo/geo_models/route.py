# .venv/Scripts/python app/models/geo/geo_models/route.py
"""
거리 최적화 초기구현모델: 격자 + A* (빠르고 단순,항상 경로 산출)
- 노드는 연안 버퍼로만 필터링 (간단/빠름)
- 1차: 간선이 연안버퍼를 가로지르면 제외(check_edge_cross=True)
- 실패 시: 간선 교차 체크 끄고 재시도(check_edge_cross=False)
- 최후: 버퍼 0으로 완화하여 재시도
입력: app/models/geo/data/portexample.csv (name,lat,lon)
출력: app/models/geo/output/route.geojson, od_ports.geojson
"""

import os, math
import networkx as nx
from networkx.exception import NetworkXNoPath
import geopandas as gpd
from shapely.geometry import Point, LineString, box
from shapely.ops import unary_union
import geodatasets as gds
from pyproj import Geod


# ---------------- 설정 ----------------
ORIGIN_NAME = "Sydney"     # CSV의 name과 일치하도록 입력
DEST_NAME   = "Auckland"

GRID_SPACING_KM = 60      # 격자 간격
COAST_BUFFER_KM = 12      # 연안 버퍼(해안선 주변 운항 금지 폭)
BOX_MARGIN_KM   = 200     # O/D 둘러싼 탐색박스 여유

CRS_WGS84 = "EPSG:4326"
CRS_METER = "EPSG:3857"    #경로 길이 계산 위해 미터 좌표 사용


# ---------------- 경로 ----------------
# 기준 폴더: app/models/geo/
ROOT_GEO   = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR   = os.path.join(ROOT_GEO, "data")
OUT_DIR    = os.path.join(ROOT_GEO, "output")
PORTS_CSV  = os.path.join(DATA_DIR, "portexample.csv")
ROUTE_PATH = os.path.join(OUT_DIR, "route.geojson")
OD_PATH    = os.path.join(OUT_DIR, "od_ports.geojson")

#data/output 폴더 없으면 생성
def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

#컬럼 표준화 , WGS84 좌표의 포인트로 변환
def load_ports(path) -> gpd.GeoDataFrame:
    import pandas as pd
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.lower()
    df = df.rename(columns={"port":"name","portname":"name",
                            "latitude":"lat","y":"lat",
                            "longitude":"lon","long":"lon","lng":"lon","x":"lon"})
    return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs=CRS_WGS84)

#name과 일치하는 항만 한 개 선택 , 없으면 에러
def pick_od(ports, name: str):
    sel = ports[ports["name"].str.lower() == name.lower()]
    if sel.empty:
        raise ValueError(f"Port '{name}' not found in {PORTS_CSV}")
    return sel.iloc[0]

def load_land_union(crs=CRS_METER):
    land = gpd.read_file(gds.get_path("naturalearth.land")).to_crs(crs)
    return unary_union(land.geometry.values)

#O/D 두 점 감싸는 바운딩박스 생성, 탐색 여유
def bbox_around(points_gdf: gpd.GeoDataFrame, margin_km: float):
    pts_m = points_gdf.to_crs(CRS_METER)
    minx, miny, maxx, maxy = pts_m.total_bounds
    m = margin_km * 1000.0
    return gpd.GeoDataFrame(geometry=[box(minx-m, miny-m, maxx+m, maxy+m)], crs=CRS_METER)

#격자 노드 생성
def generate_grid(bbox_gdf, spacing_km: float):
    spacing = spacing_km * 1000.0
    minx, miny, maxx, maxy = bbox_gdf.total_bounds
    nx_count = int((maxx - minx) // spacing) + 1
    ny_count = int((maxy - miny) // spacing) + 1
    nodes = []
    for j in range(ny_count + 1):
        y = miny + j * spacing
        if y > maxy: break
        for i in range(nx_count + 1):
            x = minx + i * spacing
            if x > maxx: break
            nodes.append((i, j, x, y))
    return nodes

#노드 필터링(노드만 연안 버퍼 바깥으로 제한 =해상 )
def filter_water_nodes(nodes, land_union, coast_km: float):
    buf = gpd.GeoSeries([land_union], crs=CRS_METER).buffer(coast_km * 1000.0).unary_union
    keep = []
    for i, j, x, y in nodes:
        if not buf.contains(Point(x, y)):
            keep.append((i, j, x, y))
    return keep

def build_graph(nodes, land_union, coast_km: float, check_edge_cross: bool):
    #8방 이웃으로 간선 연결, 간선 교차 체크는 옵션
    buf = gpd.GeoSeries([land_union], crs=CRS_METER).buffer(coast_km * 1000.0).unary_union
    grid = {(i, j): (x, y) for i, j, x, y in nodes}
    G = nx.Graph()
    for (i, j), (x, y) in grid.items():
        G.add_node((i, j), x=x, y=y)
    nbrs = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    for (i, j), (x, y) in grid.items():
        for di, dj in nbrs:
            k = (i+di, j+dj)
            if k not in grid: continue
            x2, y2 = grid[k]
            seg = LineString([(x, y), (x2, y2)])
            if check_edge_cross and buf.intersects(seg):
                continue
            G.add_edge((i, j), k, weight=seg.length)
    return G

#O/D봐표에서 가장 가까운 격자 노드 탐색
def nearest_grid_node(G: nx.Graph, xy_m):
    x0, y0 = xy_m
    best, bestd = None, float("inf")
    for n, d in G.nodes(data=True):
        dx, dy = d["x"]-x0, d["y"]-y0
        d2 = dx*dx + dy*dy
        if d2 < bestd:
            bestd, best = d2, n
    return best

#A*
def heuristic(a, b, G):
    xa, ya = G.nodes[a]["x"], G.nodes[a]["y"]
    xb, yb = G.nodes[b]["x"], G.nodes[b]["y"]
    return math.hypot(xa-xb, ya-yb)

#한 번 실행 단위(격자 간격/버퍼/간선검사) => 성공시 미터 좌표 반환
def run_once(od_gdf, land_union, grid_km, coast_km, check_edge_cross):
    od_m = od_gdf.to_crs(CRS_METER)
    bbox = bbox_around(od_m, BOX_MARGIN_KM)
    raw = generate_grid(bbox, grid_km)
    water = filter_water_nodes(raw, land_union, coast_km)
    if not water:
        return None
    G = build_graph(water, land_union, coast_km, check_edge_cross)
    o_xy = (od_m.geometry.iloc[0].x, od_m.geometry.iloc[0].y)
    d_xy = (od_m.geometry.iloc[1].x, od_m.geometry.iloc[1].y)
    o_node = nearest_grid_node(G, o_xy)
    d_node = nearest_grid_node(G, d_xy)
    try:
        path = nx.astar_path(G, o_node, d_node, heuristic=lambda a,b: heuristic(a,b,G), weight="weight")
        coords = [(G.nodes[n]["x"], G.nodes[n]["y"]) for n in path]
        return LineString(coords)
    except NetworkXNoPath:
        return None

#메인 파이프라인
def run_pipeline():
    ensure_dirs()
    ports = load_ports(PORTS_CSV)
    o = pick_od(ports, ORIGIN_NAME)
    d = pick_od(ports, DEST_NAME)
    od = gpd.GeoDataFrame([o, d], geometry="geometry", crs=CRS_WGS84)

    land_union = load_land_union(CRS_METER)

    # 1차: 간선 교차 체크 ON (간선-연안 교차 금지)
    line = run_once(od, land_union, GRID_SPACING_KM, COAST_BUFFER_KM, check_edge_cross=True)
    # 2차: 교차 체크 OFF (간선 - 연안 교차 허용)
    if line is None:
        line = run_once(od, land_union, GRID_SPACING_KM, COAST_BUFFER_KM, check_edge_cross=False)
    # 3차: 최후 — 버퍼 0 (노드도 연안 제약 해제)
    if line is None:
        line = run_once(od, land_union, GRID_SPACING_KM, coast_km=0, check_edge_cross=False)

    # 저장(WGS84)
    line_gdf_m = gpd.GeoDataFrame({"name":["A* route (simple)"]}, geometry=[line], crs=CRS_METER)
    line_gdf   = line_gdf_m.to_crs(CRS_WGS84)

    #경로 거리 계산
    try:
        g = Geod(ellps="WGS84")
        coords = list(line_gdf.geometry.iloc[0].coords)  # [(lon, lat), ...]
        dist_m = 0.0
        for (x1, y1), (x2, y2) in zip(coords, coords[1:]):
            _, _, d = g.inv(x1, y1, x2, y2)  # d: meters
            dist_m += d
        print(f"경로 거리 {dist_m / 1000:.1f}km")
    except Exception as _e:
        # 경로가 비었거나 좌표가 이상한 경우를 무시
        pass
    od_out = od[["name","geometry"]].copy()
    line_gdf.to_file(ROUTE_PATH, driver="GeoJSON")
    od_out.to_file(OD_PATH, driver="GeoJSON")
    print(f"✅ Saved: {ROUTE_PATH}")
    print(f"✅ Saved: {OD_PATH}")

if __name__ == "__main__":
    run_pipeline()


