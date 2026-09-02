"""
Forecast-informed electrolyser + residual battery strategy (core engine).

Application use cases compose this with a `SurplusForecastModel` instance
(core heuristic or infrastructure-backed adapter).
"""

from __future__ import annotations

from typing import Dict

import pandas as pd

from .controller import Controller

from smart_grid_lab.core.forecasting import SurplusForecastModel


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


class ForecastElectrolyserBatteryStrategy(Controller):
    """
    At each step: forecast surplus -> electrolyser pr -> battery absorbs remainder.

    Surplus for forecasting is taken from the precomputed `net_kw` series
    (solar power - load power), aligned to simulation timestamps.
    """

    def __init__(
        self,
        net_kw: pd.Series,
        forecast_model: SurplusForecastModel,
        electrolyser_max_kw: float,
    ) -> None:
        self._net_kw = net_kw
        self._forecast_model = forecast_model
        self._ely_max_kw = float(electrolyser_max_kw)
        self._battery_cmd: float = 0.0
        self._pr: float = 0.0

    def step(self, microgrid_state: Dict[str, float]) -> None:
        ts = pd.Timestamp(microgrid_state["solar_timestamp"])
        net = float(
            microgrid_state["solar_power"] - microgrid_state["load_power"]
        )
        tank_level = float(microgrid_state.get("hydrogen_tank_level", 0.0))

        fc = self._forecast_model.forecast_surplus_kw(self._net_kw, ts)
        pr = electrolyser_pr_from_surplus_forecast(
            fc, tank_level, self._ely_max_kw
        )
        ely_kw = pr * self._ely_max_kw
        self._battery_cmd = net - ely_kw
        self._pr = pr

    def action(self) -> Dict[str, float]:
        return {"battery": self._battery_cmd, "electrolyser": self._pr}
