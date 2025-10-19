# app/models/geo/geo_models/DistanceProvider.py
import os, math
import networkx as nx
from networkx.exception import NetworkXNoPath
import geopandas as gpd
from shapely.geometry import Point, LineString, box
from shapely.ops import unary_union
import geodatasets as gds
from pyproj import Geod
import pandas as pd
from functools import lru_cache
from typing import Optional, List

CRS_WGS84 = "EPSG:4326"
CRS_METER = "EPSG:3857"
GEOD = Geod(ellps="WGS84")
M_PER_NM = 1852.0

# ---------------------------
# CSV 로더: 인코딩 자동 판별 + 컬럼 표준화
# ---------------------------
def load_ports(path: str, encoding: Optional[str] = None) -> gpd.GeoDataFrame:
    """
    Port CSV를 robust 하게 읽어들인다.
    - encoding 지정이 없으면 utf-8-sig -> utf-8 -> cp949 -> euc-kr 순서로 폴백
    - 컬럼은 소문자/공백 제거 후 name/lat/lon 으로 표준화
    """
    tried: List[str] = []
    last_err: Optional[Exception] = None

    # 사용자가 넘기면 우선
    if encoding:
        tries = [encoding]
    else:
        tries = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]

    for enc in tries:
        try:
            df = pd.read_csv(path, encoding=enc)
            break
        except UnicodeDecodeError as e:
            tried.append(enc); last_err = e
            continue
    else:
        # 모두 실패
        msg = f"Port CSV 인코딩 감지 실패. 시도: {tried}. 파일: {path}"
        raise UnicodeDecodeError("csv-encoding", b"", 0, 1, msg) from last_err

    # 표준화: 소문자 + 공백 제거
    df.columns = df.columns.str.strip().str.lower().str.replace(r"\s+", "", regex=True)

    name_cols = ["name","port","portname","port_name","portnameen","porten","port_kor","portkor"]
    lat_cols  = ["lat","latitude","y","lat_dd","latd"]
    lon_cols  = ["lon","long","longitude","x","lon_dd","longd","lng"]

    def pick(cands):
        for c in cands:
            if c in df.columns:
                return c
        return None

    c_name = pick(name_cols)
    c_lat  = pick(lat_cols)
    c_lon  = pick(lon_cols)
    if not (c_name and c_lat and c_lon):
        raise ValueError(
            f"Port CSV 컬럼을 찾지 못함. "
            f"name 후보={name_cols}, lat 후보={lat_cols}, lon 후보={lon_cols}, "
            f"실제 컬럼={list(df.columns)}"
        )

    df = df.rename(columns={c_name: "name", c_lat: "lat", c_lon: "lon"})
    return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["lon"], df["lat"]), crs=CRS_WGS84)

def pick_port(ports, name: str):
    sel = ports[ports["name"].str.lower() == name.lower()]
    if sel.empty:
        raise ValueError(f"Port '{name}' not found in CSV")
    return sel.iloc[0]

def load_land_union(crs=CRS_METER):
    land = gpd.read_file(gds.get_path("naturalearth.land")).to_crs(crs)
    return unary_union(land.geometry.values)

def bbox_around(points_gdf: gpd.GeoDataFrame, margin_km: float):
    pts_m = points_gdf.to_crs(CRS_METER)
    minx, miny, maxx, maxy = pts_m.total_bounds
    m = margin_km * 1000.0
    return gpd.GeoDataFrame(geometry=[box(minx-m, miny-m, maxx+m, maxy+m)], crs=CRS_METER)

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

def filter_water_nodes(nodes, land_union, coast_km: float):
    buf = gpd.GeoSeries([land_union], crs=CRS_METER).buffer(coast_km * 1000.0).unary_union
    keep = []
    for i, j, x, y in nodes:
        if not buf.contains(Point(x, y)):
            keep.append((i, j, x, y))
    return keep

def build_graph(nodes, land_union, coast_km: float, check_edge_cross: bool):
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

def nearest_grid_node(G: nx.Graph, xy_m):
    x0, y0 = xy_m
    best, bestd = None, float("inf")
    for n, d in G.nodes(data=True):
        dx, dy = d["x"]-x0, d["y"]-y0
        d2 = dx*dx + dy*dy
        if d2 < bestd:
            bestd, best = d2, n
    return best

def heuristic(a, b, G):
    xa, ya = G.nodes[a]["x"], G.nodes[a]["y"]
    xb, yb = G.nodes[b]["x"], G.nodes[b]["y"]
    return math.hypot(xa-xb, ya-yb)

def _route_linestring(od_gdf, land_union, grid_km, coast_km, check_edge_cross):
    od_m = od_gdf.to_crs(CRS_METER)
    bbox = bbox_around(od_m, margin_km=200)
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
        return LineString(coords)  # meter CRS
    except NetworkXNoPath:
        return None

# ---------------------------
# 외부 공개 팩토리
# ---------------------------
def make_distance_provider_from_route(
    port_csv: str,
    *,
    grid_spacing_km: float = 60.0,
    coast_buffer_km: float = 12.0,
    port_encoding: Optional[str] = None,
):
    # ✅ 인코딩 자동판별/폴백이 적용된 로더 호출
    ports = load_ports(port_csv, encoding=port_encoding)
    land_union = load_land_union(CRS_METER)

    @lru_cache(maxsize=2048)
    def _distance_nm(origin: str, dest: str) -> float:
        o = pick_port(ports, origin)
        d = pick_port(ports, dest)
        od = gpd.GeoDataFrame([o, d], geometry="geometry", crs=CRS_WGS84)

        # 1) 간선-연안 교차 금지 → 2) 허용 → 3) 버퍼 0 완화
        line = _route_linestring(od, land_union, grid_spacing_km, coast_buffer_km, True)
        if line is None:
            line = _route_linestring(od, land_union, grid_spacing_km, coast_buffer_km, False)
        if line is None:
            line = _route_linestring(od, land_union, grid_spacing_km, 0.0, False)
        if line is None:
            raise RuntimeError("해상 경로 없음: grid/버퍼 파라미터 조정 필요")

        # 타원체 길이 합산 → nm
        line_wgs = gpd.GeoSeries([line], crs=CRS_METER).to_crs(CRS_WGS84).iloc[0]
        coords = list(line_wgs.coords)
        dist_m = 0.0
        for (x1, y1), (x2, y2) in zip(coords, coords[1:]):
            _, _, d = GEOD.inv(x1, y1, x2, y2)
            dist_m += d
        return float(dist_m / M_PER_NM)

    return _distance_nm
