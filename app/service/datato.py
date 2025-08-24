# datato.py  — (ENG 전용) origin,dest,emission,distance_km 스키마
import csv, re
from dataclasses import dataclass
from typing import List

@dataclass
class EIRow:
    origin: str           # origin port name/code
    dest: str             # destination port name/code
    distance_km: float    # km (leg distance)
    ei_per_teu_km: float  # kg CO2 / (TEU·km)

_NUM_RE = re.compile(r"[,\s]")  # '1,234' 처럼 콤마/공백 제거

def _to_float(v, name: str, i: int) -> float:
    try:
        if isinstance(v, str):
            v = _NUM_RE.sub("", v)  # '12 345' / '12,345' → '12345'
        x = float(v)
    except Exception:
        raise ValueError(f"[row {i}] '{name}' 숫자 변환 실패: {v!r}")
    return x

def load_ei_rows_from_csv(csv_path: str, encoding: str = "utf-8-sig") -> List[EIRow]:
    """
    CSV 스키마(영문, UTF-8-SIG 권장):
      origin, dest, emission, distance_km
      - emission: (구간 전체) kg/TEU
      - distance_km: km
    반환: EIRow(origin, dest, distance_km, ei_per_teu_km)
    """
    out: List[EIRow] = []
    with open(csv_path, "r", encoding=encoding, newline="") as f:
        rdr = csv.DictReader(f)
        need = ["origin", "dest", "emission", "distance_km"]
        if not rdr.fieldnames or any(c not in rdr.fieldnames for c in need):
            raise ValueError(f"필수 컬럼 누락: {need} / 실제 헤더: {rdr.fieldnames}")

        for i, r in enumerate(rdr, start=2):
            origin = (r["origin"] or "").strip()
            dest   = (r["dest"] or "").strip()
            if not origin or not dest:
                raise ValueError(f"[row {i}] origin/dest 공백")

            ei_per_teu = _to_float(r["emission"], "emission (kg/TEU)", i)     # kg/TEU (구간)
            dist_km    = _to_float(r["distance_km"], "distance_km (km)", i)   # km
            if ei_per_teu < 0 or dist_km <= 0:
                raise ValueError(f"[row {i}] 값 범위 오류(ei={ei_per_teu}, km={dist_km})")

            ei_per_teu_km = ei_per_teu / dist_km  # kg/(TEU·km)
            out.append(EIRow(
                origin=origin, dest=dest,
                distance_km=float(dist_km),
                ei_per_teu_km=float(ei_per_teu_km)
            ))
    return out
