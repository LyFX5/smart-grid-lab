#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 11:19:53 2026

@author: eduard
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from smart_grid_lab.core import (
    Time,
    Battery,
)


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


def build_time(cfg: TimeConfig) -> Time:
    return Time(
        start=pd.Timestamp(cfg.start),
        end=pd.Timestamp(cfg.end),
        step=pd.Timedelta(cfg.step_minutes, "min"),
    )


def build_battery(cfg: BatteryConfig) -> Battery:
    return Battery(
        capacity_kwh=cfg.capacity_kwh,
        max_charge_kw=cfg.max_charge_kw,
        max_discharge_kw=cfg.max_discharge_kw,
        max_charge_efficiency=cfg.max_charge_efficiency,
        max_discharge_efficiency=cfg.max_discharge_efficiency,
        initial_soc=cfg.initial_soc,
    )


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
