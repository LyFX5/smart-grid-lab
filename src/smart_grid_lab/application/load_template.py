#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 11:21:44 2026

@author: eduard
"""

import numpy as np
import pandas as pd

from smart_grid_lab.core import Time, Battery

from smart_grid_lab.domain.builders import (
    BatteryConfig,
    build_battery,
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
    pv_df = pd.read_csv("data/pv_kW.csv")
    pv_df.index = pd.to_datetime(pv_df.utc_timestamp, utc=True)
    pv_df = pv_df.drop("utc_timestamp", axis="columns")
    return pv_df[time.start : time.end][["pv"]]


def sample_load_kW(time: Time) -> pd.Series:
    load_df = pd.read_csv("data/load_kW.csv")
    load_df.index = pd.to_datetime(load_df.utc_timestamp, utc=True)
    load_df = load_df.drop("utc_timestamp", axis="columns")
    return load_df[time.start : time.end][["load"]]


def default_time() -> Time:
    return Time(
        start=pd.Timestamp(year=2016, month=3, day=15, hour=12, tz="utc"),
        end=pd.Timestamp(year=2016, month=3, day=20, hour=12, tz="utc"),
        step=pd.Timedelta(15, "min"),
    )


def default_battery() -> Battery:
    cfg = BatteryConfig(100.0, 30.0, 30.0, 0.95, 0.95, 0.5)
    return build_battery(cfg)
