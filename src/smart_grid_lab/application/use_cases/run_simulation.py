from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from smart_grid_lab import Battery, Load, SetUp, Simulation, Solar, Time


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


@dataclass
class SimulationSetup:
    """
    High-level setup used by the application layer.

    The application/UI layer works with pandas for profiles; infrastructure
    adapters can wrap this with JSON-serializable DTOs.
    """

    time: TimeConfig
    battery: BatteryConfig
    solar_profile: pd.Series
    load_profile: pd.Series


def _build_time(cfg: TimeConfig) -> Time:
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


def run_simulation(setup: SimulationSetup, use_bar: bool = False) -> pd.DataFrame:
    """
    Application-level entry point for running a microgrid simulation.

    Parameters
    ----------
    setup:
        High-level configuration with time, battery, and exogenous profiles.
    use_bar:
        Whether to display the tqdm progress bar from the core simulation.

    Returns
    -------
    pandas.DataFrame
        Trajectory indexed by timestamp, as produced by core `Simulation`.
    """

    time = _build_time(setup.time)

    components = {
        "solar": Solar(setup.solar_profile),
        "load": Load(setup.load_profile),
        "battery": _build_battery(setup.battery),
    }

    core_setup = SetUp(time=time, components=components)
    sim = Simulation(core_setup)
    result = sim.run(use_bar=use_bar)
    return result.trajectory

