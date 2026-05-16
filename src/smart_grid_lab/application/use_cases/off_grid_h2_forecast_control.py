"""
Use case: forecast-informed hydrogen production in an off-grid microgrid.

Composes **core** pieces only for the simulation loop:
`SetUp` + injectable `Simulation(..., strategy=...)`.

Forecast **contracts** live in `core.forecasting`; heuristic implementations
live there too. **Infrastructure** provides adapters (e.g. sklearn) that
implement the same contract. This module picks concrete forecast/control
variants for a scenario (clean architecture wiring from the application layer).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from smart_grid_lab.core import (
    Battery,
    Electrolyser,
    HydrogenTank,
    Load,
    Results,
    SetUp,
    Simulation,
    Solar,
    Time,
)
from smart_grid_lab.core.controllers import ForecastElectrolyserBatteryStrategy
from smart_grid_lab.core.forecasting import (
    OracleMeanSurplusForecast,
    RollingMeanBackwardSurplusForecast,
)

from smart_grid_lab.application.use_cases.demo_simulation import (
    BatteryConfig,
    battery_config_from_inputs,
    _build_battery,
)


# Must match `Solar.pv_plant_area` default until that is configurable.
_PV_PLANT_AREA_M2 = 100.0


@dataclass
class OffGridH2ForecastConfig:
    """Scenario parameters for the H2 + forecast use case."""

    forecast_horizon: int = 6
    forecast_window: int = 6
    use_oracle_forecast: bool = True
    tank_capacity_kg: float = 50.0
    tank_initial_level: float = 0.2
    electrolyser_current_max_a: float = 4.0
    temperature_ambient_c: float = 25.0


def _electrolyser_max_kw(electrolyser: Electrolyser) -> float:
    pr_saved = electrolyser.pr
    electrolyser.pr = 1.0
    try:
        return electrolyser.power() / 1000.0
    finally:
        electrolyser.pr = pr_saved


def _default_battery() -> Battery:
    cfg = BatteryConfig(100.0, 30.0, 30.0, 0.95, 0.95, 0.5)
    return _build_battery(cfg)


def run_forecast_h2_offgrid_simulation(
    time: Time,
    solar_kw: pd.Series,
    load_kw: pd.Series,
    scenario: OffGridH2ForecastConfig | None = None,
    battery: Battery | None = None,
) -> Results:
    """
    Run the core simulation engine with hydrogen components and a forecast-based strategy.

    Parameters
    ----------
    time:
        Simulation horizon and step.
    solar_kw:
        Effective solar **electrical** output (kW), same units as `Solar.power()`.
        Internally converted to irradiance via ``solar_kw / pv_plant_area`` using
        the default PV area (100 m²) to stay consistent with `Solar`.
    load_kw:
        Load power profile (kW), aligned to ``time.index_range``.
    scenario:
        Hydrogen + forecast hyperparameters.
    battery:
        Optional pre-built battery; default is a moderate residential-scale battery.
    """
    scenario = scenario or OffGridH2ForecastConfig()
    index = time.index_range
    solar_kw = solar_kw.reindex(index).astype(float)
    load_kw = load_kw.reindex(index).astype(float)
    net_kw = solar_kw - load_kw

    irradiance = solar_kw / _PV_PLANT_AREA_M2

    ely = Electrolyser(scenario.electrolyser_current_max_a, scenario.temperature_ambient_c)
    tank = HydrogenTank(scenario.tank_capacity_kg, scenario.tank_initial_level)
    batt = battery if battery is not None else _default_battery()

    components = {
        "solar": Solar(irradiance),
        "load": Load(load_kw),
        "battery": batt,
        "electrolyser": ely,
        "hydrogen_tank": tank,
    }
    setup = SetUp(time=time, components=components)

    ely_max_kw = _electrolyser_max_kw(ely)
    if scenario.use_oracle_forecast:
        forecast_model = OracleMeanSurplusForecast(scenario.forecast_horizon)
    else:
        forecast_model = RollingMeanBackwardSurplusForecast(scenario.forecast_window)

    strategy = ForecastElectrolyserBatteryStrategy(
        net_kw=net_kw,
        forecast_model=forecast_model,
        electrolyser_max_kw=ely_max_kw,
    )

    sim = Simulation(setup, strategy=strategy)
    trajectory = sim.run(use_bar=False)
    metrics = calculate_forecast_h2_metrics(trajectory, time.step)
    return Results(trajectory=trajectory, metrics=metrics)


def calculate_forecast_h2_metrics(
    trajectory: pd.DataFrame,
    step: pd.Timedelta,
) -> pd.DataFrame:
    """Summarize the forecast H₂ use case as UI-ready scalar KPIs."""
    step_h = step.total_seconds() / 3600.0

    def _energy_kwh(column: str, scale: float = 1.0) -> float | None:
        if column not in trajectory.columns:
            return None
        return round(float((trajectory[column] * scale).sum() * step_h), 3)

    final_row = trajectory.iloc[-1] if not trajectory.empty else pd.Series(dtype=float)
    metrics = {
        "solar_energy_kwh": _energy_kwh("solar_power"),
        "load_energy_kwh": _energy_kwh("load_power"),
        "electrolyser_energy_kwh": _energy_kwh("electrolyser_power", scale=1 / 1000.0),
        "hydrogen_produced_kg": None,
        "final_tank_level": None,
        "final_battery_soc": None,
        "electrolyser_degradation": None,
    }
    if "electrolyser_hydrogen_production" in trajectory.columns:
        metrics["hydrogen_produced_kg"] = round(
            float(trajectory["electrolyser_hydrogen_production"].sum() * step_h), 3
        )
    if "hydrogen_tank_level" in trajectory.columns and not trajectory.empty:
        metrics["final_tank_level"] = round(float(final_row["hydrogen_tank_level"]), 3)
    if "battery_soc" in trajectory.columns and not trajectory.empty:
        metrics["final_battery_soc"] = round(float(final_row["battery_soc"]), 3)
    if "electrolyser_degradation" in trajectory.columns and not trajectory.empty:
        metrics["electrolyser_degradation"] = round(float(final_row["electrolyser_degradation"]), 3)

    return pd.DataFrame([metrics])


def run_forecast_h2_offgrid_from_ui_battery(
    time: Time,
    solar_kw: pd.Series,
    load_kw: pd.Series,
    battery_capacity_kwh,
    battery_max_charge_kw,
    battery_max_discharge_kw,
    battery_charge_eff,
    battery_discharge_eff,
    battery_initial_soc,
    scenario: OffGridH2ForecastConfig | None = None,
) -> Results:
    """Same as `run_forecast_h2_offgrid_simulation` but builds battery from UI-like inputs."""
    cfg = battery_config_from_inputs(
        battery_capacity_kwh,
        battery_max_charge_kw,
        battery_max_discharge_kw,
        battery_charge_eff,
        battery_discharge_eff,
        battery_initial_soc,
    )
    battery = _build_battery(cfg)
    return run_forecast_h2_offgrid_simulation(time, solar_kw, load_kw, scenario, battery)
