#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 19:33:45 2026

@author: eduard
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class PVForecastModel(ABC):

    @abstractmethod
    def forecast_pv_kW(
        self, history: pd.Series, at: pd.Timestamp, horizon: pd.Timedelta
    ) -> pd.Series: ...
