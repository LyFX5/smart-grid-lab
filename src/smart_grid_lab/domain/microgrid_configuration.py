#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 09:00:18 2026

@author: eduard
"""

from __future__ import annotations

from dataclasses import dataclass

from decimal import Decimal

from pydantic_extra_types.coordinate import (
    Coordinate,
    Latitude,
    Longitude,
)


@dataclass
class TimeConfig:
    """Configuration of the simulation horizon in wall-clock time."""

    start: str  # ISO-like timestamp string
    end: str  # ISO-like timestamp string
    step_minutes: int


MICROGRID_LOCATION = Coordinate(
    latitude=Latitude(Decimal("52.37")),  # 52.132633
    longitude=Longitude(Decimal("4.90")),  # 5.291266
)


PV_AREA_M2: float = 100.0


@dataclass
class BatteryConfig:
    capacity_kwh: float
    max_charge_kw: float
    max_discharge_kw: float
    max_charge_efficiency: float
    max_discharge_efficiency: float
    initial_soc: float


@dataclass
class ForecastConfig:
    history: int = 7*24
    horizon: int = 24
