# core.py (revised)
import math, numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional, Callable

# EF(ton CO2/ton fuel) — 필요 시 사내 기준으로 교체
EF = {"HFO": 3.114, "LFO": 3.151, "MDO": 3.206, "MGO": 3.206, "LNG": 2.750}
RESERVE_RATIO = 0.05  # r

def haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dlmb = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return (c * R) / 1852.0  # meters -> nm

def nm_to_km(x: float) -> float:
    return x * 1.852

def km_to_nm(x: float) -> float:
    return x / 1.852

# RFC — 사용자가 유지하라 한 버전 그대로
def estimate_rfc(fuel_consumption_ton: float, reserve_ratio: float = RESERVE_RATIO) -> float:
    return fuel_consumption_ton * reserve_ratio

@dataclass
class TrainRow:
    D_nm: float
    fuel: str
    teu_loaded: float
    fc_obs_ton: float   # 최종 라벨(필요 시 CO2→FC로 변환)

# --- 거리 결정 로직: 제공값 > 콜백(항해그래프) > 대권거리 ---
def resolve_distance_nm(
    row: Dict,
    ports_db: Dict[str, Tuple[float, float]],
    distance_provider: Optional[Callable[[str, str], float]] = None
) -> float:
    origin = row["origin"].strip().upper()
    dest   = row["dest"].strip().upper()

    # 1) row에 직접 제공된 거리 우선
    if "distance_nm" in row and row["distance_nm"] not in (None, ""):
        d_nm = float(row["distance_nm"])
        if d_nm <= 0:
            raise ValueError(f"distance_nm <= 0: {d_nm} ({origin}->{dest})")
        return d_nm

    if "distance_km" in row and row["distance_km"] not in (None, ""):
        d_km = float(row["distance_km"])
        if d_km <= 0:
            raise ValueError(f"distance_km <= 0: {d_km} ({origin}->{dest})")
        return km_to_nm(d_km)

    # 2) 사용자 주입 콜백(향후: 항해그래프 최단경로)
    if distance_provider is not None:
        d_nm = float(distance_provider(origin, dest))
        if d_nm <= 0:
            raise ValueError(f"distance_provider returned <= 0 for {origin}->{dest}")
        return d_nm

    # 3) 대권거리(기본)
    if origin not in ports_db or dest not in ports_db:
        raise KeyError(f"ports_db에 포트가 없습니다: origin={origin}, dest={dest}")
    lat1, lon1 = ports_db[origin]; lat2, lon2 = ports_db[dest]
    d_nm = haversine_nm(lat1, lon1, lat2, lon2)
    if d_nm <= 0:
        raise ValueError(f"haversine_nm <= 0 for {origin}->{dest} (coords? {ports_db[origin]} -> {ports_db[dest]})")
    return d_nm

def prepare_training_rows(
    raw_rows: List[Dict],
    ports_db: Dict[str, Tuple[float,float]],
    ef_table: Dict[str,float] = EF,
    reserve_ratio: float = RESERVE_RATIO,
    distance_provider: Optional[Callable[[str, str], float]] = None,
    allow_unknown_fuel_for_fc: bool = True
) -> List[TrainRow]:
    """
    raw_rows 필수키:
      - origin, dest, fuel, teu_loaded
      - 라벨 중 하나: fc_obs_ton | co2_obs_ton
      - (선택) distance_nm | distance_km  # 있으면 우선 사용
    """
    out: List[TrainRow] = []
    for r in raw_rows:
        # 기본 필드
        if any(k not in r for k in ("origin","dest","fuel","teu_loaded")):
            raise KeyError(f"필수 키 누락 in row: {r}")
        fuel = str(r["fuel"]).strip().upper()
        teu  = float(r["teu_loaded"])
        if teu <= 0:
            raise ValueError(f"teu_loaded <= 0: {teu} (row={r})")

        # 거리 결정(제공값 > 콜백 > 대권)
        D_nm = resolve_distance_nm(r, ports_db, distance_provider)

        # 라벨 결정
        fc: Optional[float] = None
        if "fc_obs_ton" in r and r["fc_obs_ton"] not in (None, ""):
            fc = float(r["fc_obs_ton"])
        elif "co2_obs_ton" in r and r["co2_obs_ton"] not in (None, ""):
            # CO2 → FC 환산: EF*(1-r)
            if fuel not in ef_table:
                raise KeyError(f"EF 미정의 연료 '{fuel}' (CO2→FC 환산 필요). ef_table 갱신 요망.")
            ef = float(ef_table[fuel])
            co2 = float(r["co2_obs_ton"])
            if co2 < 0:
                raise ValueError(f"co2_obs_ton < 0: {co2}")
            denom = ef * (1 - reserve_ratio)
            if denom <= 0:
                raise ValueError(f"EF*(1-r) <= 0: EF={ef}, r={reserve_ratio}")
            fc = co2 / denom
        else:
            raise ValueError("라벨 누락: fc_obs_ton 또는 co2_obs_ton 중 하나가 필요합니다.")

        if fc is None or fc < 0:
            raise ValueError(f"fc_obs_ton(환산 포함) < 0: {fc} (row={r})")

        # 연료 미정 허용 옵션(FC 라벨만 있을 때)
        if (fuel not in ef_table) and not allow_unknown_fuel_for_fc and ("co2_obs_ton" in r and r["co2_obs_ton"] not in (None, "")):
            # 위 CO2 분기는 이미 EF 체크함. 여기선 안전망.
            raise KeyError(f"알 수 없는 연료 '{fuel}'")

        out.append(TrainRow(D_nm=D_nm, fuel=fuel, teu_loaded=teu, fc_obs_ton=float(fc)))
    return out

def build_fuel_vocab(rows: List[TrainRow]) -> List[str]:
    return sorted(list({r.fuel for r in rows}))

def row_to_features(r: TrainRow, fuel_vocab: List[str], use_teu: bool=True):
    feats = [r.D_nm]
    if use_teu:
        feats.append(r.teu_loaded)
    feats += [1.0 if r.fuel == f else 0.0 for f in fuel_vocab]
    return np.array(feats, float)

def build_Xy(rows: List[TrainRow], fuel_vocab: List[str], use_teu: bool=True):
    X = np.vstack([row_to_features(r, fuel_vocab, use_teu) for r in rows])
    y = np.array([r.fc_obs_ton for r in rows], float)
    return X, y
