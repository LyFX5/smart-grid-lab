#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 11:21:23 2026

@author: eduard
"""

from smart_grid_lab.domain.builders import (
    TimeConfig,
    BatteryConfig,
)


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

    return TimeConfig(start, end, step_val)


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
