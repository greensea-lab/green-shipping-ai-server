# app/service/datato.py

import csv, re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class EIRow:
    origin: str
    dest: str
    distance_km: float
    ei_per_teu_km: float

_NUM_RE = re.compile(r"[,\s]")

def _to_float(v, name: str, i: int) -> float:
    try:
        if isinstance(v, str):
            v = _NUM_RE.sub("", v)
        x = float(v)
    except Exception:
        raise ValueError(f"[row {i}] '{name}' 숫자 변환 실패: {v!r}")
    return x

def _pick_col(cols_set, *candidates) -> Optional[str]:
    for cand in candidates:
        if cand and cand in cols_set:
            return cand
    return None

def load_ei_rows_from_csv(csv_path: str, encoding: str = "utf-8-sig") -> List[EIRow]:
    """
    다양한 헤더 변형을 자동 인식:
      - origin: origin, from, origin_port, load_port, loading_port ...
      - dest: dest, to, destination, discharge_port, unloading_port ...
      - 거리: distance_km / dist_km / km / distance  (또는 distance_nm / nm → km 변환)
      - 배출량:
          (A) emission(kg/TEU, 구간 전체)  → ei_per_teu_km = emission / distance_km
          (B) ei_per_teu_km / ei_kg_teu_km / kg_per_teu_km  → 그대로 사용
    최소 필요 정보: origin, dest, 그리고 (A 또는 B 중 하나) + 거리
    """
    out: List[EIRow] = []
    with open(csv_path, "r", encoding=encoding, newline="") as f:
        rdr = csv.DictReader(f)
        if not rdr.fieldnames:
            raise ValueError("CSV 헤더를 읽을 수 없습니다.")
        # 정규화된 컬럼명 세트(소문자, 공백/언더스코어 제거)
        raw_cols = [c for c in rdr.fieldnames if c]
        norm_map = {c: re.sub(r"[ _]", "", c.strip().lower()) for c in raw_cols}
        inv = {}
        for orig, norm in norm_map.items():
            # 동일한 정규화 키가 여러 번 나오면 첫 것을 유지
            inv.setdefault(norm, orig)
        cols = set(norm_map.values())

        # 필수 컬럼 탐색
        c_origin = _pick_col(cols, "origin", "from", "originport", "loadport", "loadingport", "출발", "출발지")
        c_dest   = _pick_col(cols, "dest", "to", "destination", "dischargeport", "unloadingport", "도착", "도착지")
        if not c_origin or not c_dest:
            raise ValueError(f"필수 컬럼(origin/dest) 누락. 실제 헤더: {raw_cols}")

        # 거리 컬럼(km 우선, nm 있으면 변환)
        c_dist_km = _pick_col(cols, "distancekm", "distkm", "km", "distance", "routekm")
        c_dist_nm = _pick_col(cols, "distancenm", "distnm", "nm", "routenm")
        if not c_dist_km and not c_dist_nm:
            raise ValueError(f"거리 컬럼(distance_km 또는 distance_nm) 누락. 실제 헤더: {raw_cols}")

        # 배출 강도/배출량 컬럼
        c_ei_km = _pick_col(cols, "eiperteukm", "eikgperteukm", "kgperteukm", "kgteukm")
        c_emission = _pick_col(cols, "emission", "emissionkgperteu", "kgperteu", "co2teu", "co2perteu")
        if not c_ei_km and not c_emission:
            raise ValueError(f"배출 정보 컬럼(ei_per_teu_km 또는 emission[kg/TEU]) 누락. 실제 헤더: {raw_cols}")

        for i, r in enumerate(rdr, start=2):
            # 원본 키에서 값 꺼내기(정규화 키로 역매핑)
            def V(norm_key):
                key = inv.get(norm_key)
                return (r.get(key) if key is not None else None)

            origin = (V(c_origin) or "").strip()
            dest   = (V(c_dest)   or "").strip()
            if not origin or not dest:
                raise ValueError(f"[row {i}] origin/dest 공백")

            # 거리(km)
            if c_dist_km:
                dist_km = _to_float(V(c_dist_km), "distance_km", i)
            else:
                dist_nm = _to_float(V(c_dist_nm), "distance_nm", i)
                dist_km = dist_nm * 1.852
            if dist_km <= 0:
                raise ValueError(f"[row {i}] distance_km <= 0")

            # EI(kg/TEU·km)
            if c_ei_km:
                ei_per_teu_km = _to_float(V(c_ei_km), "ei_per_teu_km", i)
            else:
                emission = _to_float(V(c_emission), "emission (kg/TEU, 구간)", i)
                ei_per_teu_km = emission / dist_km
            if ei_per_teu_km < 0:
                raise ValueError(f"[row {i}] ei_per_teu_km < 0")

            out.append(EIRow(
                origin=origin,
                dest=dest,
                distance_km=float(dist_km),
                ei_per_teu_km=float(ei_per_teu_km),
            ))
    return out
