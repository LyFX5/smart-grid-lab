"""Forecast adapters backed by external inference (infrastructure layer)."""

from .load_gblinear import OpenSTEFGBLinearLoadForecastAdapter
from .pv_gblinear import OpenSTEFGBLinearPVForecastAdapter

__all__ = [
    "OpenSTEFGBLinearLoadForecastAdapter",
    "OpenSTEFGBLinearPVForecastAdapter",
]
