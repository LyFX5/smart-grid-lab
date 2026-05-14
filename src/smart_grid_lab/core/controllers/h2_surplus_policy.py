"""Policy helpers for electrolyser dispatch (core, used by strategies)."""

from __future__ import annotations


def electrolyser_pr_from_surplus_forecast(
    forecast_surplus_kw: float,
    tank_level: float,
    electrolyser_max_kw: float,
    *,
    tank_full: float = 0.95,
    surplus_deadband_kw: float = 0.5,
    tank_derate_from: float = 0.85,
) -> float:
    if electrolyser_max_kw <= 0:
        return 0.0
    if tank_level >= tank_full:
        return 0.0
    if forecast_surplus_kw < surplus_deadband_kw:
        return 0.0

    desired_kw = min(max(forecast_surplus_kw, 0.0), electrolyser_max_kw)
    pr = desired_kw / electrolyser_max_kw

    if tank_level > tank_derate_from:
        span = max(tank_full - tank_derate_from, 1e-6)
        pr *= max(0.0, min(1.0, (tank_full - tank_level) / span))

    return float(max(0.0, min(1.0, pr)))
