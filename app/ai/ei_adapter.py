from __future__ import annotations

from typing import Any, Dict, Optional

from app.service.deps import get_distance_provider, get_model_pack
from app.service.feature import EIPayload, prepare_inputs


def predict_ei_metrics(origin: str, dest: str, teu_loaded: float, fuel: str) -> Dict[str, Any]:
    """
    Run EI prediction using internal service modules and return a flat metrics dict
    suitable to be merged into AI Metrics.

    Returns keys (when available):
      - origin, dest, fuel, teu_loaded
      - route_distance_nm, route_distance_km
      - ei_kg_per_teu_km, co2_ton, fc_ton
      - notes (optional)

    On failure (e.g., model missing), returns best-effort distance info and a note.
    """
    # Build distance provider (may fail offline or missing CSV)
    try:
        distance_provider = get_distance_provider()
    except Exception as e_dp:
        distance_provider = None  # degrade gracefully

    try:
        # Prepare inputs (also validates and computes distances/Ef lookup)
        payload = EIPayload(
            origin=origin, dest=dest, teu_loaded=teu_loaded, fuel=fuel
        )
        if distance_provider is None:
            raise RuntimeError("Distance provider unavailable")
        prep = prepare_inputs(payload, distance_provider)

        # Load model pack & predict
        pack = get_model_pack()
        # Lazy import to avoid hard dependency during non-EI flows
        from app.service.train_xgb import predict_from_ei  # type: ignore
        out = predict_from_ei(
            pack=pack,
            origin=prep["origin"],
            dest=prep["dest"],
            teu_loaded=prep["teu_loaded"],
            distance_provider=distance_provider,
        )

        return {
            "origin": prep["origin"],
            "dest": prep["dest"],
            "fuel": prep["fuel"],
            "teu_loaded": prep["teu_loaded"],
            "route_distance_nm": prep["distance_nm"],
            "route_distance_km": out["distance_km"],
            "ei_kg_per_teu_km": out["ei_kg_per_teu_km"],
            "co2_ton": out["co2_ton"],
            "fc_ton": out["fc_ton"],
        }
    except Exception as e:
        # Best-effort: try to compute distance only
        if distance_provider is not None:
            try:
                d_nm = float(distance_provider(origin, dest))
            except Exception:
                d_nm = None
        else:
            d_nm = None
        return {
            "origin": origin,
            "dest": dest,
            "fuel": fuel,
            "teu_loaded": teu_loaded,
            "route_distance_nm": d_nm,
            "notes": f"EI prediction unavailable: {e}",
        }
