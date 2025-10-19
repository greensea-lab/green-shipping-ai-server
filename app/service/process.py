# process.py — EI-residual 파이프라인과 호환되도록 수정
from typing import Dict, Tuple, Optional, Callable
from app.service.train_xgb import TrainedEIResidual, predict_from_ei
from app.service.data_set import nm_to_km  # 필요하면 유지

# (origin, dest) -> nm
DistanceProvider = Callable[[str, str], float]

def _provider_from_args(
    distance_nm: Optional[float],
    distance_km: Optional[float],
    fallback: Optional[DistanceProvider],
) -> DistanceProvider:
    """
    인자로 직접 준 거리(distance_nm/km)가 우선이고,
    없으면 fallback distance_provider를 사용하도록 감싸는 래퍼.
    """
    if distance_nm is not None:
        d_nm = float(distance_nm)
        if d_nm <= 0:
            raise ValueError(f"유효하지 않은 거리(nm): {d_nm}")
        return lambda _o, _d: d_nm

    if distance_km is not None:
        d_km = float(distance_km)
        if d_km <= 0:
            raise ValueError(f"유효하지 않은 거리(km): {d_km}")
        return lambda _o, _d: d_km / 1.852

    if fallback is None:
        raise ValueError(
            "거리 소스가 없습니다. distance_nm 또는 distance_km를 제공하거나 "
            "distance_provider(항해그래프 콜백)를 넘겨주세요."
        )
    return fallback

def predict_fc_co2_ei(
    model_pack: TrainedEIResidual,                # ✅ 변경: TrainedFCModel -> TrainedEIResidual
    ports_db: Dict[str, Tuple[float, float]],     # 유지(호출부 호환용, 내부에선 사용하지 않음)
    origin: str,
    dest: str,
    teu_loaded: float,
    fuel: str,                                    # EI-Residual에서는 fuel 미사용(남겨도 무방)
    *,
    distance_nm: Optional[float] = None,
    distance_km: Optional[float] = None,
    distance_provider: Optional[DistanceProvider] = None
) -> Dict[str, float]:
    """
    EI-Residual 모델을 사용한 일관된 예측 함수.
    - 거리 우선순위: distance_nm > distance_km > distance_provider
    - 내부에서 predict_from_ei 호출
    """
    dp = _provider_from_args(distance_nm, distance_km, distance_provider)

    out = predict_from_ei(
        pack=model_pack,
        origin=origin,
        dest=dest,
        teu_loaded=float(teu_loaded),
        distance_provider=dp
    )
    # out: {"distance_km","ei_kg_per_teu_km","co2_ton","fc_ton"}

    # 필요하면 distance_nm도 함께 반환(호환성용)
    d_nm = (distance_nm if distance_nm is not None
            else (distance_km / 1.852 if distance_km is not None
                  else out["distance_km"] / 1.852))
    out["distance_nm"] = float(d_nm)
    return out
