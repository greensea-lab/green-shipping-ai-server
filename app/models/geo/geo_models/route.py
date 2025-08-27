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
from shapely.ops import unary_union, nearest_points
from shapely.prepared import prep
import geodatasets as gds
from pyproj import Geod


# ---------------- 설정 ----------------
ORIGIN_NAME = "Pusan"     # CSV의 name과 일치하도록 입력
DEST_NAME   = "Sydney"

# 기본 격자/버퍼
GRID_SPACING_KM = 60       # 기존 격자 간격(호환성 유지용)
COAST_BUFFER_KM = 12       # 연안 버퍼(해안선 주변 운항 금지 폭)
BOX_MARGIN_KM   = 200      # O/D 둘러싼 탐색박스 여유

# 옵션 A: 단계적(러프→정밀) 벡터 라우팅 파라미터
COARSE_GRID_KM   = 120     # 1단계 러프 격자
FINE_GRID_KM     = 25      # 2단계 정밀 격자
CORRIDOR_KM      = 100     # 러프 경로 주변 코리더 폭
EXPAND_STEP_KM   = 100     # 실패 시 BBox 확장 단위
PENALTY_BAND_KM  = 50      # 연안 인근 패널티 적용 거리(버퍼 외측)
PENALTY_FACTOR   = 2.5     # 최대 추가 가중(밴드 경계에서 선형 0→factor)

# 로컬 연결(끝단 안정) 파라미터
CONNECT_MAX_RADIUS_KM = 80  # O/D에서 그래프까지 연결 탐색 최대 반경
CONNECT_EDGES_MAX     = 6   # 연결할 최대 간선 수(안정적 연결을 위해 복수)

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

def make_coast_buffer(land_union, coast_km: float):
    """육지 유니온을 기준으로 연안 버퍼 폴리곤과 PreparedGeometry 생성."""
    buf_geom = gpd.GeoSeries([land_union], crs=CRS_METER).buffer(coast_km * 1000.0).unary_union
    return buf_geom, prep(buf_geom)

def snap_points_to_water(od_gdf_m: gpd.GeoDataFrame, buf_geom, bbox_geom):
    """O/D가 버퍼 내부(즉, 금지구역)이면 BBox 내 수역으로 스냅.
    - 수역 = bbox_geom - buf_geom
    """
    water = bbox_geom.difference(buf_geom)
    new_geoms = []
    for pt in od_gdf_m.geometry:
        if not buf_geom.contains(pt):
            new_geoms.append(pt)
            continue
        # 버퍼 내부이면 최근접 수역 점으로 스냅
        np1, np2 = nearest_points(pt, water)
        new_geoms.append(np2)
    out = od_gdf_m.copy()
    out["geometry"] = new_geoms
    return out

def penalty_multiplier_for_point(p: Point, buf_geom, band_m: float, factor: float):
    if band_m <= 0:
        return 1.0
    d = p.distance(buf_geom)
    if d >= band_m:
        return 1.0
    return 1.0 + (factor * (band_m - d) / band_m)

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
def filter_water_nodes(nodes, buf_prepared, mask_geom=None):
    """연안 버퍼 밖(=수역)이고, 선택적으로 mask_geom 내부인 노드만 유지."""
    keep = []
    has_mask = mask_geom is not None
    for i, j, x, y in nodes:
        p = Point(x, y)
        if buf_prepared.contains(p):
            continue
        if has_mask and not mask_geom.contains(p):
            continue
        keep.append((i, j, x, y))
    return keep

def build_graph(nodes, buf_geom, buf_prepared, check_edge_cross: bool,
                penalty_band_km: float | None = None, penalty_factor: float = 2.0):
    """8방 이웃 연결. 선택적으로 연안 인접 패널티를 가중치에 반영."""
    grid = {(i, j): (x, y) for i, j, x, y in nodes}
    G = nx.Graph()
    for (i, j), (x, y) in grid.items():
        G.add_node((i, j), x=x, y=y)
    nbrs = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    band_m = (penalty_band_km or 0) * 1000.0
    for (i, j), (x, y) in grid.items():
        for di, dj in nbrs:
            k = (i+di, j+dj)
            if k not in grid:
                continue
            x2, y2 = grid[k]
            seg = LineString([(x, y), (x2, y2)])
            if check_edge_cross and buf_prepared.intersects(seg):
                continue
            w = seg.length
            if band_m > 0:
                mid = Point((x + x2) * 0.5, (y + y2) * 0.5)
                # 버퍼 경계에서의 거리로 선형 패널티 적용
                mult = penalty_multiplier_for_point(mid, buf_geom, band_m, penalty_factor)
                w *= mult
            G.add_edge((i, j), k, weight=w)
    return G

def connect_point_to_graph(G: nx.Graph, name: str, xy, buf_geom, buf_prepared,
                           penalty_band_km: float | None, penalty_factor: float,
                           max_radius_km: float = CONNECT_MAX_RADIUS_KM,
                           max_edges: int = CONNECT_EDGES_MAX,
                           conn_check_edge_cross: bool = True) -> bool:
    """그래프에 포인트 노드를 추가하고, 교차 금지 조건으로 주변 노드와 연결.
    - 간선 가중치에 연안 패널티를 반영.
    - 반환: 하나 이상 간선을 연결했는지 여부.
    """
    x0, y0 = xy
    node_name = (name,)
    if node_name not in G:
        G.add_node(node_name, x=x0, y=y0)
    # 후보 노드 거리 계산
    cand = []
    for n, d in G.nodes(data=True):
        if isinstance(n, tuple) and len(n) == 1:
            # 이미 추가한 특수 노드(O/D) 제외
            continue
        dx = d["x"] - x0
        dy = d["y"] - y0
        dist = math.hypot(dx, dy)
        cand.append((dist, n, d))
    cand.sort(key=lambda t: t[0])
    added = 0
    limit = (max_radius_km or 0) * 1000.0
    band_m = (penalty_band_km or 0) * 1000.0
    for dist, n, d in cand:
        if limit > 0 and dist > limit:
            break
        seg = LineString([(x0, y0), (d["x"], d["y"])])
        if conn_check_edge_cross and buf_prepared.intersects(seg):
            continue
        w = dist
        mid = seg.interpolate(0.5, normalized=True)
        mult = penalty_multiplier_for_point(mid, buf_geom, band_m, penalty_factor)
        w *= mult
        G.add_edge(node_name, n, weight=w)
        added += 1
        if added >= (max_edges or 1):
            break
    return added > 0

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
def run_once(od_gdf, land_union, grid_km, coast_km, check_edge_cross,
             bbox_margin_km: float | None = None,
             mask_geom=None,
             penalty_band_km: float | None = None,
             penalty_factor: float = PENALTY_FACTOR):
    od_m = od_gdf.to_crs(CRS_METER)
    bbox = bbox_around(od_m, bbox_margin_km or BOX_MARGIN_KM)
    buf_geom, buf_prepared = make_coast_buffer(land_union, coast_km)
    # 필요 시 O/D를 수역으로 스냅
    od_m = snap_points_to_water(od_m, buf_geom, bbox.unary_union)
    raw = generate_grid(bbox, grid_km)
    water = filter_water_nodes(raw, buf_prepared, mask_geom)
    if not water:
        return None
    G = build_graph(water, buf_geom, buf_prepared, check_edge_cross,
                    penalty_band_km=penalty_band_km, penalty_factor=penalty_factor)
    o_xy = (od_m.geometry.iloc[0].x, od_m.geometry.iloc[0].y)
    d_xy = (od_m.geometry.iloc[1].x, od_m.geometry.iloc[1].y)
    # O/D를 그래프 노드로 추가하고, 교차 금지 조건으로 연결
    ok_o = connect_point_to_graph(G, "O", o_xy, buf_geom, buf_prepared,
                                  penalty_band_km, penalty_factor,
                                  max_radius_km=CONNECT_MAX_RADIUS_KM,
                                  max_edges=CONNECT_EDGES_MAX,
                                  conn_check_edge_cross=check_edge_cross)
    ok_d = connect_point_to_graph(G, "D", d_xy, buf_geom, buf_prepared,
                                  penalty_band_km, penalty_factor,
                                  max_radius_km=CONNECT_MAX_RADIUS_KM,
                                  max_edges=CONNECT_EDGES_MAX,
                                  conn_check_edge_cross=check_edge_cross)
    if not (ok_o and ok_d):
        return None
    try:
        start = ("O",)
        goal = ("D",)
        path = nx.astar_path(G, start, goal, heuristic=lambda a,b: heuristic(a,b,G), weight="weight")
        coords = [(G.nodes[n]["x"], G.nodes[n]["y"]) for n in path]
        return LineString(coords)
    except NetworkXNoPath:
        return None

#메인 파이프라인
def run_pipeline():
    import time
    t0 = time.time()
    ensure_dirs()
    ports = load_ports(PORTS_CSV)
    o = pick_od(ports, ORIGIN_NAME)
    d = pick_od(ports, DEST_NAME)
    od = gpd.GeoDataFrame([o, d], geometry="geometry", crs=CRS_WGS84)

    land_union = load_land_union(CRS_METER)

    # 단계 1: 러프 경로(여러 폴백 포함)
    t_coarse0 = time.time()
    line = None
    for expand in [0, EXPAND_STEP_KM, 2 * EXPAND_STEP_KM]:
        for coast_km in [COAST_BUFFER_KM, max(COAST_BUFFER_KM - 4, 0), max(COAST_BUFFER_KM - 8, 0)]:
            # 엄격 모드 먼저 시도
            line = run_once(
                od, land_union, COARSE_GRID_KM, coast_km, check_edge_cross=True,
                bbox_margin_km=BOX_MARGIN_KM + expand,
                penalty_band_km=PENALTY_BAND_KM, penalty_factor=PENALTY_FACTOR,
            )
            if line is not None:
                break
            # 간선 교차 허용으로 재시도(러프에서만)
            line = run_once(
                od, land_union, COARSE_GRID_KM, coast_km, check_edge_cross=False,
                bbox_margin_km=BOX_MARGIN_KM + expand,
                penalty_band_km=PENALTY_BAND_KM, penalty_factor=PENALTY_FACTOR,
            )
            if line is not None:
                break
        if line is not None:
            break
    # 최후의 수단: 버퍼 0
    if line is None:
        line = run_once(
            od, land_union, COARSE_GRID_KM, coast_km=0, check_edge_cross=False,
            bbox_margin_km=BOX_MARGIN_KM + 2 * EXPAND_STEP_KM,
            penalty_band_km=None,
        )
    t_coarse1 = time.time()

    if line is None:
        raise RuntimeError("경로 탐색 실패: 설정을 완화해도 경로를 찾지 못했습니다.")

    # 단계 2: 코리더 내 정밀 재탐색
    corridor = gpd.GeoSeries([line], crs=CRS_METER).buffer(CORRIDOR_KM * 1000.0).unary_union
    fine = None
    t_fine0 = time.time()
    for coast_km in [COAST_BUFFER_KM, max(COAST_BUFFER_KM - 4, 0), max(COAST_BUFFER_KM - 8, 0), 0]:
        # 정밀 단계는 간선-연안 교차 금지를 우선
        fine = run_once(
            od, land_union, FINE_GRID_KM, coast_km, check_edge_cross=True,
            bbox_margin_km=BOX_MARGIN_KM, mask_geom=corridor,
            penalty_band_km=PENALTY_BAND_KM, penalty_factor=PENALTY_FACTOR,
        )
        if fine is not None:
            break
        # 실패 시에만 제한 완화
        fine = run_once(
            od, land_union, FINE_GRID_KM, coast_km, check_edge_cross=False,
            bbox_margin_km=BOX_MARGIN_KM, mask_geom=corridor,
            penalty_band_km=PENALTY_BAND_KM, penalty_factor=PENALTY_FACTOR,
        )
        if fine is not None:
            break
    t_fine1 = time.time()
    final_line = fine or line

    # 저장(WGS84)
    line_gdf_m = gpd.GeoDataFrame({"name":["A* route (coarse-to-fine)"]}, geometry=[final_line], crs=CRS_METER)
    line_gdf   = line_gdf_m.to_crs(CRS_WGS84)

    # 스냅된 O/D(WGS84) 내보내기
    od_m = gpd.GeoDataFrame({"name": [ORIGIN_NAME, DEST_NAME]},
                             geometry=[Point(final_line.coords[0]), Point(final_line.coords[-1])],
                             crs=CRS_METER)
    od_out = od_m.to_crs(CRS_WGS84)

    # 경로 거리 계산
    try:
        g = Geod(ellps="WGS84")
        coords = list(line_gdf.geometry.iloc[0].coords)  # [(lon, lat), ...]
        dist_m = 0.0
        for (x1, y1), (x2, y2) in zip(coords, coords[1:]):
            _, _, d = g.inv(x1, y1, x2, y2)  # d: meters
            dist_m += d
        print(f"경로 거리 {dist_m / 1000:.1f}km")
    except Exception:
        pass

    line_gdf.to_file(ROUTE_PATH, driver="GeoJSON")
    od_out.to_file(OD_PATH, driver="GeoJSON")
    print(f"✅ Saved: {ROUTE_PATH}")
    print(f"✅ Saved: {OD_PATH}")
    # 시간 측정 로그
    print(f"⏱️ Coarse phase: {t_coarse1 - t_coarse0:.2f}s, Fine phase: {t_fine1 - t_fine0:.2f}s, Total: {time.time() - t0:.2f}s")

if __name__ == "__main__":
    # 간단한 CLI 인자 처리: --origin/-o, --dest/-d
    try:
        import argparse
        parser = argparse.ArgumentParser(description="Sea route finder (coarse-to-fine A*)")
        parser.add_argument("-o", "--origin", help="Origin port name (as in CSV)")
        parser.add_argument("-d", "--dest", help="Destination port name (as in CSV)")
        args = parser.parse_args()
        if args.origin:
            ORIGIN_NAME = args.origin
        if args.dest:
            DEST_NAME = args.dest
    except Exception:
        pass
    run_pipeline()