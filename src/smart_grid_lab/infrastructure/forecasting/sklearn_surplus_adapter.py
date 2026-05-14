"""
Sklearn (or similar) surplus forecast adapter — inference lives here.

Implements the core `SurplusForecastModel` contract. Wire a trained model
path when available; until then this falls back to persistence at `at`.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd

from smart_grid_lab.core.forecasting import SurplusForecastModel


class SklearnSurplusForecastAdapter(SurplusForecastModel):
    def __init__(self, model_path: Optional[str] = None) -> None:
        self._model_path = model_path

    def forecast_surplus_kw(self, net_kw: pd.Series, at: pd.Timestamp) -> float:
        if self._model_path is None:
            return float(net_kw.loc[at])
        raise NotImplementedError(
            "SklearnSurplusForecastAdapter: wire model load + predict mapping "
            f"for path {self._model_path!r}."
        )
