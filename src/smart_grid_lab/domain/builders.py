#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 11:19:53 2026

@author: eduard
"""

import pandas as pd

from smart_grid_lab.core import (
    Time,
    Battery,
)

from .microgrid_configuration import TimeConfig, BatteryConfig


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
