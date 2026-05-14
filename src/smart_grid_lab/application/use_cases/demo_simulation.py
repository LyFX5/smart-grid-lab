from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from smart_grid_lab.core import Time, Solar, Load, Battery, SetUp, Results, Simulation


@dataclass
class TimeConfig:
    """Configuration of the simulation horizon in wall-clock time."""

    start: str  # ISO-like timestamp string
    end: str  # ISO-like timestamp string
    step_minutes: int


@dataclass
class BatteryConfig:
    capacity_kwh: float
    max_charge_kw: float
    max_discharge_kw: float
    max_charge_efficiency: float
    max_discharge_efficiency: float
    initial_soc: float


def time_config_from_inputs(
    start: str | None,
    end: str | None,
    step_minutes: int | float | None,
) -> TimeConfig:
    """
    Build a TimeConfig object from UI inputs, with safe fallbacks.
    """
    if not start:
        start = "2026-03-15 12:00:00"
    if not end:
        end = "2026-03-20 12:00:00"
    try:
        step_val = int(step_minutes) if step_minutes is not None else 10
    except (TypeError, ValueError):
        step_val = 10

    return TimeConfig(start, end, step_minutes)


def battery_config_from_inputs(
    capacity_kwh,
    max_charge_kw,
    max_discharge_kw,
    charge_eff,
    discharge_eff,
    initial_soc,
) -> BatteryConfig:
    def _num(v, default):
        if v is None:
            return default
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    capacity_kwh = _num(capacity_kwh, 100.0)
    max_charge_kw = _num(max_charge_kw, 30.0)
    max_discharge_kw = _num(max_discharge_kw, 30.0)
    charge_eff = _num(charge_eff, 0.95)
    discharge_eff = _num(discharge_eff, 0.95)
    initial_soc = _num(initial_soc, 0.5)
    return BatteryConfig(
        capacity_kwh,
        max_charge_kw,
        max_discharge_kw,
        charge_eff,
        discharge_eff,
        initial_soc,
    )


def build_time(cfg: TimeConfig) -> Time:
    return Time(
        start=pd.Timestamp(cfg.start),
        end=pd.Timestamp(cfg.end),
        step=pd.Timedelta(cfg.step_minutes, "min"),
    )


def _build_battery(cfg: BatteryConfig) -> Battery:
    return Battery(
        capacity_kwh=cfg.capacity_kwh,
        max_charge_kw=cfg.max_charge_kw,
        max_discharge_kw=cfg.max_discharge_kw,
        max_charge_efficiency=cfg.max_charge_efficiency,
        max_discharge_efficiency=cfg.max_discharge_efficiency,
        initial_soc=cfg.initial_soc,
    )


def setup_from_inputs(
    time_cfg: TimeConfig,
    solar_series: pd.Series,
    load_series: pd.Series,
    battery_cfg: BatteryConfig,
) -> SetUp:
    time = build_time(time_cfg)
    components = {
        "solar": Solar(solar_series),
        "load": Load(load_series),
        "battery": _build_battery(battery_cfg),
    }
    return SetUp(time, components)


def run_simulation(setup: SetUp) -> Results:
    simulation = Simulation(setup)
    trajectory = simulation.run(use_bar=False)
    metrics = simulation.calculate_metrics(trajectory)
    return Results(trajectory, metrics)
