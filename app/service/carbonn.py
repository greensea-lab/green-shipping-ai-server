#탄소 배출량 모델
def calculate_fuel_consumption(sfoc_g_per_kwh: float, k: float, distance_nm: float, speed_knots: float) -> float:
    """
    프로펠러 법칙 기반 연료소모량 계산 (ton)
    """
    fuel_tons = (sfoc_g_per_kwh * k * distance_nm * (speed_knots ** 2)) / 1_000_000
    return fuel_tons

def estimate_rfc(fuel_consumption_ton: float, reserve_ratio: float = 0.05) -> float:
    """
    연료 잔존량 (RFC) 계산
    """
    return fuel_consumption_ton * reserve_ratio

def calculate_co2_emission(fc_ton: float, ef: float, reserve_ratio: float = 0.05) -> float:
    """
    탄소배출량 계산 (ton)
    - ef: Emission Factor (ton CO2 / ton fuel), HFO 기준 3.114
    """
    rfc = estimate_rfc(fc_ton, reserve_ratio)
    return ef * (fc_ton - rfc)
