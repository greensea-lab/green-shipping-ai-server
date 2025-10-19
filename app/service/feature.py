# app/service/feature.py
#train_eval는 학습데이터로 이게 실제로 쓰이는 코드
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Callable, Dict

# (origin, dest) -> distance_nm
DistanceProvider = Callable[[str, str], float]

EF_TABLE: Dict[str, float] = {
    # ton CO2 / ton fuel (data_set.py와 동일 테이블)
    "HFO": 3.114, "LFO": 3.151, "MDO": 3.206, "MGO": 3.206, "LNG": 2.750,
}

def nm_to_km(x: float) -> float: return float(x) * 1.852

@dataclass
class EIPayload:
    origin: str
    dest: str
    teu_loaded: float
    fuel: str  # ⬅️ 필수로 받음

    # 아래 옵션은 남겨두면 확장 쉬움(베이스라인/로그용)
    speed_knots: Optional[float] = None
    sfoc_g_per_kwh: Optional[float] = None
    k: Optional[float] = None

    def validate(self) -> None:
        if not self.origin or not self.dest:
            raise ValueError("origin/dest는 비어 있을 수 없습니다.")
        if self.teu_loaded is None or float(self.teu_loaded) <= 0:
            raise ValueError("teu_loaded는 0보다 커야 합니다.")
        if not self.fuel:
            raise ValueError("fuel은 필수입니다.")
        fu = self.fuel.strip().upper()
        if fu not in EF_TABLE:
            raise ValueError(f"지원하지 않는 연료: {self.fuel} "
                             f"(허용: {', '.join(EF_TABLE.keys())})")

    def normalized(self) -> "EIPayload":
        return EIPayload(
            origin=self.origin.strip(),
            dest=self.dest.strip(),
            teu_loaded=float(self.teu_loaded),
            fuel=self.fuel.strip().upper(),
            speed_knots=(14.0 if self.speed_knots is None else float(self.speed_knots)),
            sfoc_g_per_kwh=(175.0 if self.sfoc_g_per_kwh is None else float(self.sfoc_g_per_kwh)),
            k=(1.0 if self.k is None else float(self.k)),
        )

def prepare_inputs(payload: EIPayload, distance_provider: DistanceProvider):
    """
    - 입력 검증/정규화
    - distance_provider로 거리 산출 (nm, km 동시 반환)
    - 연료(EF) 확인
    """
    payload.validate()
    pl = payload.normalized()

    d_nm = float(distance_provider(pl.origin, pl.dest))
    if d_nm <= 0:
        raise ValueError(f"거리 계산 실패: {d_nm}")
    d_km = nm_to_km(d_nm)

    ef = EF_TABLE[pl.fuel]  # ton CO2 / ton fuel

    return {
        "origin": pl.origin,
        "dest": pl.dest,
        "teu_loaded": pl.teu_loaded,
        "fuel": pl.fuel,
        "distance_nm": d_nm,
        "distance_km": d_km,
        "ef_ton_per_ton": ef,          # ⬅️ 연료별 EF (FC 환산 시 사용)
        "speed_knots": pl.speed_knots, # (옵션) 베이스라인 확장 대비
        "sfoc_g_per_kwh": pl.sfoc_g_per_kwh,
        "k": pl.k,
    }
