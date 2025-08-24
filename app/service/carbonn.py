def fuel_consumption_ton_nm(
    sfoc_g_per_kwh: float,
    distance_nm: float,
    speed_kn: float,
    alpha: float = 1.0,
) -> float:
    """FC[ton] = (SFOC * α * D_nm * v_kn^2) / 1e6"""
    return (sfoc_g_per_kwh * alpha * distance_nm * (speed_kn ** 2)) / 1_000_000

def emission_intensity_kg_per_teu_km_knots(
    sfoc_g_per_kwh: float,
    speed_kn: float,
    teu_loaded: float,
    ef_ton_per_ton: float,
    reserve_ratio: float = 0.05,
    alpha: float = 1.0,
) -> float:
    """
    EI = [EF*(1-r)*SFOC*α*v_kn^2] / [1852 * TEU_loaded]
    """
    if teu_loaded <= 0:
        raise ValueError("teu_loaded > 0 필요")
    return (ef_ton_per_ton * (1 - reserve_ratio) * sfoc_g_per_kwh * alpha * (speed_kn ** 2)) / (1852.0 * teu_loaded)