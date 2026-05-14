"""Forecast adapters backed by external inference (infrastructure layer)."""

from smart_grid_lab.infrastructure.forecasting.sklearn_surplus_adapter import (
    SklearnSurplusForecastAdapter,
)

__all__ = ["SklearnSurplusForecastAdapter"]
