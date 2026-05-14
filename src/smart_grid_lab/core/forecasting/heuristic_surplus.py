"""Reference surplus forecasters (core, no external inference dependencies)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .surplus import SurplusForecastModel


class OracleMeanSurplusForecast(SurplusForecastModel):
    """Mean of the next `horizon` actual net values after `at` (non-causal oracle)."""

    def __init__(self, horizon: int) -> None:
        if horizon < 1:
            raise ValueError("horizon must be >= 1")
        self.horizon = horizon

    def forecast_surplus_kw(self, net_kw: pd.Series, at: pd.Timestamp) -> float:
        idx = net_kw.index.get_loc(at)
        if isinstance(idx, slice):
            raise ValueError("non-unique index")
        if isinstance(idx, np.ndarray):
            idx = int(idx[0])
        else:
            idx = int(idx)
        end = min(len(net_kw), idx + 1 + self.horizon)
        future = net_kw.iloc[idx + 1 : end]
        if future.empty:
            return float(net_kw.iloc[idx])
        return float(future.mean())


class RollingMeanBackwardSurplusForecast(SurplusForecastModel):
    """Mean of the last `window` samples up to and including `at` (causal)."""

    def __init__(self, window: int) -> None:
        if window < 1:
            raise ValueError("window must be >= 1")
        self.window = window

    def forecast_surplus_kw(self, net_kw: pd.Series, at: pd.Timestamp) -> float:
        idx = net_kw.index.get_loc(at)
        if isinstance(idx, slice):
            raise ValueError("non-unique index")
        if isinstance(idx, np.ndarray):
            idx = int(idx[0])
        else:
            idx = int(idx)
        start = max(0, idx - self.window + 1)
        window_series = net_kw.iloc[start : idx + 1]
        return float(window_series.mean())
