"""
Use case: forecast-informed hydrogen production in an off-grid microgrid.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from smart_grid_lab.core import (
    Time,
    Solar,
    Load,
    Battery,
    Electrolyser,
    HydrogenTank,
    SetUp,
    Simulation,
    Results,
)

from smart_grid_lab.core.controllers import Strategy

from smart_grid_lab.application.demo_simulation import (
    BatteryConfig,
    battery_config_from_inputs,
    _build_battery,
)

# Must match `Solar.pv_plant_area` default until that is configurable.
_PV_PLANT_AREA_M2 = 100.0


def _default_time() -> Time:
    return Time(
        start=pd.Timestamp(year=2026, month=3, day=15, hour=12),
        end=pd.Timestamp(year=2026, month=3, day=20, hour=12),
        step=pd.Timedelta(10, "min"),
    )


def _synthetic_solar_kW(time: Time) -> pd.Series:
    time_index = time.index_range
    hour = time_index.hour
    # day_of_year = time_index.dayofyear # may be usefull
    ghi = np.maximum(0, 800 * np.sin(np.pi * (hour - 6) / 12))
    ghi += np.random.normal(0, 50, len(ghi))
    ghi /= 1000
    return pd.Series(data=ghi, index=time_index)


def _synthetic_load_kW(time: Time) -> pd.Series:
    periods = time.periods
    time_index = time.index_range
    np.random.seed(42)
    base_load = 20 + 10 * np.sin(2 * np.pi * np.arange(periods) / 24)
    load = np.maximum(5, base_load + np.random.normal(0, 3, periods))
    return pd.Series(data=load, index=time_index)


def sample_solar_kW(time: Time) -> pd.Series:
    # TODO pull from prepared
    ...


def sample_load_kW(time: Time) -> pd.Series:
    # TODO pull from prepared
    ...


@dataclass
class H2Config:
    tank_capacity_kg: float = 50.0
    tank_initial_level: float = 0.2
    electrolyser_current_max_a: float = 4.0
    temperature_ambient_c: float = 25.0


@dataclass
class ForecastConfig:
    forecast_horizon: int = 6
    forecast_window: int = 6
    use_oracle_forecast: bool = True


def _default_battery() -> Battery:
    cfg = BatteryConfig(100.0, 30.0, 30.0, 0.95, 0.95, 0.5)
    return _build_battery(cfg)


def _default_strategy() -> Strategy:
    ...  # TODO build strategy
    return ...


def run_simulation(
    time: Time | None = None,
    solar_kw: pd.Series | None = None,
    load_kw: pd.Series | None = None,
    battery: Battery | None = None,
    h2_config: H2Config | None = None,
    strategy: Strategy | None = None,
    use_bar=False,
) -> Results:
    """
    Run the core simulation engine with hydrogen components and a forecast-based strategy.

    Parameters
    ----------
    ...
    """

    time = time if time is not None else _default_time()
    index = time.index_range

    solar_kw = solar_kw if solar_kw is not None else _synthetic_solar_kW(time)
    solar_kw = solar_kw.reindex(index).astype(float)

    load_kw = load_kw if load_kw is not None else _synthetic_load_kW(time)
    load_kw = load_kw.reindex(index).astype(float)

    # net_kw = solar_kw - load_kw # TODO need by forecaster needed by strateegy

    irradiance = solar_kw / _PV_PLANT_AREA_M2

    batt = battery if battery is not None else _default_battery()

    h2_config = h2_config if h2_config is not None else H2Config()
    ely = Electrolyser(
        h2_config.electrolyser_current_max_a, h2_config.temperature_ambient_c
    )
    tank = HydrogenTank(
        h2_config.tank_capacity_kg, h2_config.tank_initial_level
    )

    components = {
        "solar": Solar(irradiance),
        "load": Load(load_kw),
        "battery": batt,
        "electrolyser": ely,
        "hydrogen_tank": tank,
    }

    setup = SetUp(time=time, components=components)

    strategy = strategy if strategy is not None else _default_strategy()

    sim = Simulation(setup, strategy=strategy)

    trajectory = sim.run(use_bar=use_bar)
    metrics = calculate_metrics(trajectory, time.step)

    return Results(trajectory=trajectory, metrics=metrics)


def calculate_metrics(
    trajectory: pd.DataFrame,
    step: pd.Timedelta,
) -> pd.DataFrame:
    # TODO re-implement
    """Summarize the forecast H₂ use case as UI-ready scalar KPIs."""
    step_h = step.total_seconds() / 3600.0

    def _energy_kwh(column: str, scale: float = 1.0) -> float | None:
        if column not in trajectory.columns:
            return None
        return round(float((trajectory[column] * scale).sum() * step_h), 3)

    final_row = (
        trajectory.iloc[-1] if not trajectory.empty else pd.Series(dtype=float)
    )
    metrics = {
        "solar_energy_kwh": _energy_kwh("solar_power"),
        "load_energy_kwh": _energy_kwh("load_power"),
        "electrolyser_energy_kwh": _energy_kwh(
            "electrolyser_power", scale=1 / 1000.0
        ),
        "hydrogen_produced_kg": None,
        "final_tank_level": None,
        "final_battery_soc": None,
        "electrolyser_degradation": None,
    }
    if "electrolyser_hydrogen_production" in trajectory.columns:
        metrics["hydrogen_produced_kg"] = round(
            float(
                trajectory["electrolyser_hydrogen_production"].sum() * step_h
            ),
            3,
        )
    if "hydrogen_tank_level" in trajectory.columns and not trajectory.empty:
        metrics["final_tank_level"] = round(
            float(final_row["hydrogen_tank_level"]), 3
        )
    if "battery_soc" in trajectory.columns and not trajectory.empty:
        metrics["final_battery_soc"] = round(
            float(final_row["battery_soc"]), 3
        )
    if (
        "electrolyser_degradation" in trajectory.columns
        and not trajectory.empty
    ):
        metrics["electrolyser_degradation"] = round(
            float(final_row["electrolyser_degradation"]), 3
        )

    return pd.DataFrame([metrics])


def run_from_ui(
    time: Time,
    solar_kw: pd.Series,
    load_kw: pd.Series,
    battery_capacity_kwh,
    battery_max_charge_kw,
    battery_max_discharge_kw,
    battery_charge_eff,
    battery_discharge_eff,
    battery_initial_soc,
    # TODO build h2_config, forecasters and strategy choice from ui
    h2_config,
    strategy_config,
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

    strategy = None  # TODO read strategy from strategy_config

    return run_simulation(
        time, solar_kw, load_kw, battery, h2_config, strategy
    )
