#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 09:54:36 2026

@author: eduard
"""

import pandas as pd

from smart_grid_lab.core.forecasting import LoadForecastModel


class PerfectLoadForecaster(LoadForecastModel):

    def __init__(self, profile: pd.Series) -> None:
        self.profile = profile

    def forecast_load_kW(
        self,
        at: pd.Timestamp,
        horizon: pd.Timedelta,
    ) -> float:
        return self.profile[at : at + horizon]
