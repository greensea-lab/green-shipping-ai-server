"""
sea_map_router.py — GeoPandas/NetworkX 기반 해상 최단거리 DistanceProvider

요약
- 직선(대권) 금지: 육지/금지구역을 피하는 해상 경로만 허용
- 포트 좌표는 CSV(코드/이름/위도/경도)에서 자동 탐지하여 조회
- distance_provider(origin, dest) -> nm 시그니처 제공

필요 데이터
- 육지 폴리곤: Natural Earth/OSM 등 (Shapefile 또는 GeoJSON, EPSG:4326 권장)
- (옵션) 금지구역 폴리곤 (EPSG:4326)
- 포트 DB CSV (UTF-8 권장, CP949도 자동 감지)

주의
- step_deg 작을수록 정확↑/속도↓
- corridor_buffer_km는 우회 경로를 포함할 만큼 충분히
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict

import numpy as np
import pandas as pd
import networkx as nx
import geopandas as gpd
from shapely.geometry import Point, LineString
from shapely.ops import unary_union
from shapely.prepared import prep
from pyproj import Geod

GEOD = Geod(ellps="WGS84")
M_PER_NM = 1852.0


# -----------------------------
# 거리 유틸
# -----------------------------
def geodesic_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """정확한 타원체(WSG84) 지오데식 거리(m)."""
    _, _, d = GEOD.inv(lon1, lat1, lon2, lat2)
    return float(d)


def geodesic_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return geodesic_m(lat1, lon1, lat2, lon2) / M_PER_NM


# -----------------------------
# Geo 데이터 준비: 육지/금지구역
# -----------------------------
@dataclass
class SeaMap:
    land_path: str
    coast_buffer_km: float = 0.0
    nogo_path: Optional[str] = None

    def __post_init__(self):
        land = gpd.read_file(self.land_path).to_crs(4326)
        if self.coast_buffer_km > 0:
            land = (
                land.to_crs(3857)
                .buffer(self.coast_buffer_km * 1000)
                .to_crs(4326)
                .to_frame("geometry")
            )
        self.land_union = unary_union(land.geometry)
        self.land_prep = prep(self.land_union)

        if self.nogo_path:
            nogo = gpd.read_file(self.nogo_path).to_crs(4326)
            self.nogo_union = unary_union(nogo.geometry)
            self.nogo_prep = prep(self.nogo_union)
        else:
            self.nogo_union = None
            self.nogo_prep = None

    @staticmethod
    def _corridor_bbox(
        start: Tuple[float, float],
        goal: Tuple[float, float],
        buffer_km: float,
    ) -> Tuple[float, float, float, float]:
        # 대권 경로 주변을 버퍼링한 탐색 회랑(bounding box)
        lonlats = GEOD.npts(start[1], start[0], goal[1], goal[0], 300)
        coords = [(start[1], start[0])] + lonlats + [(goal[1], goal[0])]
        line = gpd.GeoSeries([LineString(coords)], crs=4326)
        buf = line.to_crs(3857).buffer(buffer_km * 1000).to_crs(4326)
        minx, miny, maxx, maxy = buf.total_bounds
        return float(miny), float(maxy), float(minx), float(maxx)  # (lat_min, lat_max, lon_min, lon_max)

    def build_graph(
        self,
        start: Tuple[float, float],
        goal: Tuple[float, float],
        *,
        corridor_buffer_km: float = 500.0,
        step_deg: float = 0.5,
        connect_8: bool = True,
        max_edge_km: float = 120.0,
        terminal_k: int = 16,
    ) -> Tuple[nx.Graph, Tuple[float, float, float, float]]:
        lat_min, lat_max, lon_min, lon_max = self._corridor_bbox(start, goal, corridor_buffer_km)
        lats = np.arange(lat_min, lat_max + 1e-9, step_deg)
        lons = np.arange(lon_min, lon_max + 1e-9, step_deg)

        G = nx.Graph()
        grid_ids: Dict[Tuple[int, int], int] = {}

        # 노드 생성 (육지/금지 제외)
        for i, lat in enumerate(lats):
            for j, lon in enumerate(lons):
                p = Point(lon, lat)
                if self.land_prep.contains(p):
                    continue
                if self.nogo_prep and self.nogo_prep.contains(p):
                    continue
                nid = len(G)
                G.add_node(nid, lat=float(lat), lon=float(lon))
                grid_ids[(i, j)] = nid

        # 인접 연결(4/8방향)
        dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if connect_8:
            dirs += [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for (i, j), u in grid_ids.items():
            lat_u, lon_u = lats[i], lons[j]
            for di, dj in dirs:
                ii, jj = i + di, j + dj
                v = grid_ids.get((ii, jj))
                if v is None or u >= v:
                    continue
                lat_v, lon_v = lats[ii], lons[jj]
                seg = LineString([(lon_u, lat_u), (lon_v, lat_v)])
                if self.land_prep.intersects(seg):
                    continue
                if self.nogo_prep and self.nogo_prep.intersects(seg):
                    continue
                d_m = geodesic_m(lat_u, lon_u, lat_v, lon_v)
                if max_edge_km and d_m > max_edge_km * 1000:
                    continue
                G.add_edge(u, v, dist_m=d_m, weight=d_m, kind="sea")

        # 단말(시작/종료) 스냅 연결
        for tid, (tlat, tlon) in [("START", start), ("GOAL", goal)]:
            G.add_node(tid, lat=float(tlat), lon=float(tlon), kind="terminal")
            dists = []
            for nid, d in G.nodes(data=True):
                if isinstance(nid, str):
                    continue
                dm = geodesic_m(tlat, tlon, d["lat"], d["lon"])
                dists.append((dm, nid))
            for dm, nid in sorted(dists, key=lambda x: x[0])[:terminal_k]:
                seg = LineString([(tlon, tlat), (G.nodes[nid]['lon'], G.nodes[nid]['lat'])])
                if self.land_prep.intersects(seg):
                    continue
                if self.nogo_prep and self.nogo_prep.intersects(seg):
                    continue
                G.add_edge(tid, nid, dist_m=dm, weight=dm, kind="terminal_link")

        return G, (lat_min, lat_max, lon_min, lon_max)


# -----------------------------
# 포트 DB: CSV 로더 (인코딩 자동 감지)
# -----------------------------
def _read_csv_auto(path: str) -> pd.DataFrame:
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr", "latin1"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    # 마지막 시도
    return pd.read_csv(path, encoding="cp949")


class PortDB:
    def __init__(self, csv_path: str):
        self.df = _read_csv_auto(csv_path)

        # 컬럼 자동 탐지
        self.col_code = self._find_col(["code", "port_code", "PORT", "port", "코드"])
        self.col_name = self._find_col(["name", "port_name", "NAME", "항구", "이름"])
        self.col_lat = self._find_col(["lat", "latitude", "위도"])
        self.col_lon = self._find_col(["lon", "lng", "longitude", "경도"])

        if not (self.col_lat and self.col_lon and (self.col_code or self.col_name)):
            raise ValueError("port_DB 컬럼을 찾을 수 없습니다. (필요: 위도/경도, 코드 또는 이름)")

        # 대문자 정규화 컬럼 준비
        if self.col_code:
            self.df["_CODE_UP"] = self.df[self.col_code].astype(str).str.strip().str.upper()
        if self.col_name:
            self.df["_NAME_UP"] = self.df[self.col_name].astype(str).str.strip().str.upper()

    def _find_col(self, candidates: List[str]) -> Optional[str]:
        s = set(c.lower() for c in self.df.columns)
        for c in candidates:
            if c.lower() in s:
                for real in self.df.columns:
                    if real.lower() == c.lower():
                        return real
        return None

    def lookup(self, key: str) -> Tuple[float, float]:
        key_up = (key or "").strip().upper()
        df = self.df
        mask = False
        if "_CODE_UP" in df.columns:
            mask = mask | (df["_CODE_UP"] == key_up)
        if "_NAME_UP" in df.columns:
            mask = mask | (df["_NAME_UP"] == key_up)
        hit = df[mask]
        if hit.empty:
            raise KeyError(f"포트 검색 실패: {key}")
        row = hit.iloc[0]
        return float(row[self.col_lat]), float(row[self.col_lon])


# -----------------------------
# 라우터: DistanceProvider 구현
# -----------------------------
@dataclass
class SeaRouter:
    sea_map: SeaMap
    port_db: PortDB
    corridor_buffer_km: float = 500.0
    step_deg: float = 0.5
    connect_8: bool = True
    max_edge_km: float = 120.0
    terminal_k: int = 16

    # 수동 캐시: (ORIGIN, DEST) -> distance_nm
    _cache: dict = field(default_factory=dict, init=False, repr=False)

    def distance_nm(self, origin: str, dest: str) -> float:
        if not origin or not dest:
            raise ValueError("origin/dest 필요")

        o = origin.strip().upper()
        d = dest.strip().upper()
        if o == d:
            return 0.0

        key = (o, d)
        if key in self._cache:
            return self._cache[key]

        # 포트 좌표 조회
        start = self.port_db.lookup(o)
        goal = self.port_db.lookup(d)

        # 그래프 구성
        G, _ = self.sea_map.build_graph(
            start,
            goal,
            corridor_buffer_km=self.corridor_buffer_km,
            step_deg=self.step_deg,
            connect_8=self.connect_8,
            max_edge_km=self.max_edge_km,
            terminal_k=self.terminal_k,
        )

        # 최단 경로
        try:
            path = nx.shortest_path(G, source="START", target="GOAL", weight="weight")
        except nx.NetworkXNoPath:
            raise RuntimeError("해상 경로 없음: 파라미터(버퍼/격자/연결) 조정 필요")

        # 거리(m) 합산 → nm 변환
        total_m = 0.0
        for u, v in zip(path, path[1:]):
            total_m += float(G.edges[u, v]["dist_m"])

        dist_nm = total_m / M_PER_NM
        self._cache[key] = dist_nm
        return dist_nm


# -----------------------------
# 외부에서 바로 provider 만들 때 쓰는 헬퍼
# -----------------------------
def make_distance_provider_from_sea(
    port_db_csv: str,
    land_path: str,
    nogo_path: Optional[str] = None,
    *,
    coast_buffer_km: float = 0.0,
    corridor_buffer_km: float = 800.0,
    step_deg: float = 0.5,
    connect_8: bool = True,
    max_edge_km: float = 150.0,
    terminal_k: int = 24,
):
    pdb = PortDB(port_db_csv)
    smap = SeaMap(land_path=land_path, coast_buffer_km=coast_buffer_km, nogo_path=nogo_path)
    router = SeaRouter(
        sea_map=smap,
        port_db=pdb,
        corridor_buffer_km=corridor_buffer_km,
        step_deg=step_deg,
        connect_8=connect_8,
        max_edge_km=max_edge_km,
        terminal_k=terminal_k,
    )

    def provider(origin: str, dest: str) -> float:
        return router.distance_nm(origin, dest)  # nm

    return provider


# -----------------------------
# 사용 예 (python -m app.service.sea)
# -----------------------------
if __name__ == "__main__":
    # 환경변수로 경로 주입 가능 (기본값은 현재 디렉터리)
    PORT_DB_CSV = os.getenv("PORT_DB", "./port_DB.csv")
    LAND_PATH = os.getenv("LAND_PATH", "./land.geojson")
    NOGO_PATH = os.getenv("NOGO_PATH", "") or None

    port_db = PortDB(PORT_DB_CSV)
    sea_map = SeaMap(land_path=LAND_PATH, coast_buffer_km=0.0, nogo_path=NOGO_PATH)
    router = SeaRouter(
        sea_map=sea_map,
        port_db=port_db,
        corridor_buffer_km=800.0,  # 대양 횡단 시 넉넉히
        step_deg=0.5,
        connect_8=True,
        max_edge_km=150.0,
        terminal_k=24,
    )

    o, d = "PUSAN", "ROTTERDAM"
    try:
        dist = router.distance_nm(o, d)
        print(f"{o} → {d} 해상 최단거리: {dist:.1f} nm")
    except Exception as e:
        print("오류:", e)
