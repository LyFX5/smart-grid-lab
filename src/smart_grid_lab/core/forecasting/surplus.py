"""Forecast model contracts for surplus power (core definitions)."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class SurplusForecastModel(ABC):
    """
    Predicts expected **electrical surplus** (kW) available for flexible loads.

    Implementations may be pure heuristics in core, or adapters backed by
    trained models in infrastructure.
    """

    @abstractmethod
    def forecast_surplus_kw(
        self,
        net_kw: pd.Series,
        at: pd.Timestamp,
    ) -> float:
        """Return scalar forecast of surplus (kW) at decision time `at`."""
