# sea_map.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, List
import numpy as np
import networkx as nx
import geopandas as gpd
from shapely.geometry import Point, LineString
from shapely.ops import unary_union
from shapely.prepared import prep
from pyproj import Geod

GEOD = Geod(ellps="WGS84")

def geodesic_m(lat1, lon1, lat2, lon2) -> float:
    _, _, d = GEOD.inv(lon1, lat1, lon2, lat2)
    return float(d)

@dataclass
class SeaMap:
    land_path: str
    coast_buffer_km: float = 0.0
    nogo_path: Optional[str] = None

    def __post_init__(self):
        land = gpd.read_file(self.land_path).to_crs(4326)
        if self.coast_buffer_km > 0:
            land = land.to_crs(3857).buffer(self.coast_buffer_km * 1000).to_crs(4326).to_frame("geometry")
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
    def _corridor_bbox(start, goal, buffer_km: float) -> Tuple[float,float,float,float]:
        lonlats = GEOD.npts(start[1], start[0], goal[1], goal[0], 300)
        coords = [(start[1], start[0])] + lonlats + [(goal[1], goal[0])]
        line = gpd.GeoSeries([LineString(coords)], crs=4326)
        buf = line.to_crs(3857).buffer(buffer_km * 1000).to_crs(4326)
        minx, miny, maxx, maxy = buf.total_bounds
        return float(miny), float(maxy), float(minx), float(maxx)  # (lat_min, lat_max, lon_min, lon_max)

    def build_graph(self,
        start: Tuple[float,float], goal: Tuple[float,float],
        *, corridor_buffer_km: float,
        step_deg: float, connect_8: bool, max_edge_km: float,
        terminal_k: int
    ) -> Tuple[nx.Graph, Tuple[float,float,float,float]]:
        lat_min, lat_max, lon_min, lon_max = self._corridor_bbox(start, goal, corridor_buffer_km)
        lats = np.arange(lat_min, lat_max + 1e-9, step_deg)
        lons = np.arange(lon_min, lon_max + 1e-9, step_deg)

        G = nx.Graph()
        grid_ids = {}
        # 노드 생성(육지/금지구역 제외)
        for i, lat in enumerate(lats):
            for j, lon in enumerate(lons):
                p = Point(lon, lat)
                if self.land_prep.contains(p):  # 육지면 스킵
                    continue
                if self.nogo_prep and self.nogo_prep.contains(p):
                    continue
                nid = len(G)
                G.add_node(nid, lat=float(lat), lon=float(lon))
                grid_ids[(i, j)] = nid

        # 이웃 연결
        dirs = [(-1,0),(1,0),(0,-1),(0,1)]
        if connect_8:
            dirs += [(-1,-1),(-1,1),(1,-1),(1,1)]

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

        # 단말 스냅 연결
        for tid, (tlat, tlon) in [("START", start), ("GOAL", goal)]:
            G.add_node(tid, lat=float(tlat), lon=float(tlon), kind="terminal")
            # 간단 kNN: 모든 그리드와 거리 계산 후 상위 k
            dists = []
            for nid, d in G.nodes(data=True):
                if isinstance(nid, str):  # START/GOAL 제외
                    continue
                dm = geodesic_m(tlat, tlon, d["lat"], d["lon"])
                dists.append((dm, nid))
            for dm, nid in sorted(dists, key=lambda x: x[0])[:terminal_k]:
                seg = LineString([(tlon, tlat), (G.nodes[nid]["lon"], G.nodes[nid]["lat"])])
                if self.land_prep.intersects(seg):
                    continue
                if self.nogo_prep and self.nogo_prep.intersects(seg):
                    continue
                G.add_edge(tid, nid, dist_m=dm, weight=dm, kind="terminal_link")

        return G, (lat_min, lat_max, lon_min, lon_max)
