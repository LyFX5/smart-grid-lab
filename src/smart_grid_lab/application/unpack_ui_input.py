#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 11:21:23 2026

@author: eduard
"""

from smart_grid_lab.domain.microgrid_configuration import (
    TimeConfig,
    BatteryConfig,
)


def time_config_from_inputs(
    start: str | None,
    end: str | None,
    step_minutes: int | float | None,
) -> TimeConfig:

    default_config = TimeConfig()

    if not start:
        start = default_config.start
    if not end:
        end = default_config.end
    try:
        step_val = (
            int(step_minutes)
            if step_minutes is not None
            else default_config.step_minutes
        )
    except (TypeError, ValueError):
        step_val = default_config.step_minutes

    return TimeConfig(start, end, step_val)


def battery_config_from_inputs(
    capacity_kwh,
    max_charge_kw,
    max_discharge_kw,
    max_charge_efficiency,
    max_discharge_efficiency,
    initial_soc,
) -> BatteryConfig:
    def _num(v, default):
        if v is None:
            return default
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    default_config = BatteryConfig()

    capacity_kwh = _num(capacity_kwh, default_config.capacity_kwh)
    max_charge_kw = _num(max_charge_kw, default_config.max_charge_kw)
    max_discharge_kw = _num(max_discharge_kw, default_config.max_discharge_kw)
    max_charge_efficiency = _num(
        max_charge_efficiency, default_config.max_charge_efficiency
    )
    max_discharge_efficiency = _num(
        max_discharge_efficiency, default_config.max_discharge_efficiency
    )
    initial_soc = _num(initial_soc, default_config.initial_soc)

    return BatteryConfig(
        capacity_kwh,
        max_charge_kw,
        max_discharge_kw,
        max_charge_efficiency,
        max_discharge_efficiency,
        initial_soc,
    )


"""
def _positive_int(value, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, parsed)


def _float_or_default(value, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
"""
