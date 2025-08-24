from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any

import requests

from app.config import settings


@dataclass
class SpeedChangeInput:
    distance_nm: float
    base_speed_knots: float
    new_speed_knots: float
    sfoc_g_per_kwh: Optional[float] = None
    k: Optional[float] = None
    vessel_type: Optional[str] = None


@dataclass
class SpeedChangeResult:
    fc_base_ton: Optional[float]
    fc_new_ton: Optional[float]
    co2_base_ton: Optional[float]
    co2_new_ton: Optional[float]
    co2_reduction_pct: Optional[float]
    time_base_hours: Optional[float]
    time_new_hours: Optional[float]
    time_delta_hours: Optional[float]
    time_increase_pct: Optional[float]
    assumptions: list[str]
    notes: Optional[str] = None


class SimAdapter:
    """Adapter for calling internal simulation API.

    If SIM_API_BASE is not configured, uses a local stub calculation and marks it as such.
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or settings.sim_api_base
        self.api_key = api_key or settings.sim_api_key

    def simulate_speed_change(self, payload: SpeedChangeInput) -> SpeedChangeResult:
        if not self.base_url:
            return self._simulate_stub(payload)

        url = self.base_url.rstrip('/') + "/sim/speed-change"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        data: Dict[str, Any] = {
            "distance_nm": payload.distance_nm,
            "base_speed_knots": payload.base_speed_knots,
            "new_speed_knots": payload.new_speed_knots,
            "sfoc_g_per_kwh": payload.sfoc_g_per_kwh,
            "k": payload.k,
            "vessel_type": payload.vessel_type,
        }
        try:
            resp = requests.post(url, json=data, headers=headers, timeout=10)
            resp.raise_for_status()
            r = resp.json()
            return SpeedChangeResult(
                fc_base_ton=r.get("fc_base_ton"),
                fc_new_ton=r.get("fc_new_ton"),
                co2_base_ton=r.get("co2_base_ton"),
                co2_new_ton=r.get("co2_new_ton"),
                co2_reduction_pct=r.get("co2_reduction_pct"),
                time_base_hours=r.get("time_base_hours"),
                time_new_hours=r.get("time_new_hours"),
                time_delta_hours=r.get("time_delta_hours"),
                time_increase_pct=r.get("time_increase_pct"),
                assumptions=r.get("assumptions", []),
                notes=r.get("notes"),
            )
        except Exception as e:
            # Fall back to stub on failure, with explicit note
            res = self._simulate_stub(payload)
            res.notes = f"Stub result due to API error: {e}"
            return res

    def _simulate_stub(self, payload: SpeedChangeInput) -> SpeedChangeResult:
        # Minimal stub using provided formula; clearly indicate as stub
        assumptions = [
            "This is a stubbed calculation (internal API not configured).",
            "EF=3.114, reserve_ratio=0.05"
        ]
        ef = 3.114
        reserve = 0.05
        # Guard against invalid values
        d = max(0.0, float(payload.distance_nm))
        v0 = max(0.1, float(payload.base_speed_knots))
        v1 = max(0.1, float(payload.new_speed_knots))

        # Optional coefficients
        sfoc = float(payload.sfoc_g_per_kwh) if payload.sfoc_g_per_kwh is not None else None
        k = float(payload.k) if payload.k is not None else None

        fc0 = fc1 = None
        if sfoc is not None and k is not None:
            fc0 = (sfoc * k * d * (v0 ** 2)) / 1_000_000
            fc1 = (sfoc * k * d * (v1 ** 2)) / 1_000_000
            assumptions.append("Used provided SFOC and k for fuel estimation.")
        else:
            assumptions.append("SFOC/k missing, fuel not estimated in stub.")

        c0 = c1 = red = None
        if fc0 is not None and fc1 is not None:
            c0 = ef * (fc0 - fc0 * reserve)
            c1 = ef * (fc1 - fc1 * reserve)
            red = ((c0 - c1) / c0 * 100.0) if c0 > 0 else 0.0

        t0 = d / v0 if v0 > 0 else None
        t1 = d / v1 if v1 > 0 else None
        dt = (t1 - t0) if (t1 is not None and t0 is not None) else None
        tip = ((dt / t0) * 100.0) if (dt is not None and t0 and t0 > 0) else None

        return SpeedChangeResult(
            fc_base_ton=fc0,
            fc_new_ton=fc1,
            co2_base_ton=c0,
            co2_new_ton=c1,
            co2_reduction_pct=red,
            time_base_hours=t0,
            time_new_hours=t1,
            time_delta_hours=dt,
            time_increase_pct=tip,
            assumptions=assumptions,
            notes="Stub calculation"
        )

