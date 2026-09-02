"""Forecast adapters backed by external inference (infrastructure layer)."""

from .sklearn_surplus_adapter import SklearnSurplusForecastAdapter
from .openstef_load_adapter import OpenSTEFGBLinearLoadForecastAdapter
from .openstef_pv_adapter import OpenSTEFGBLinearPVForecastAdapter
from .pv_physics import (
    PVSystemConfig,
    ghi_to_pv_linear,
)

__all__ = [
    "SklearnSurplusForecastAdapter",
    "OpenSTEFGBLinearLoadForecastAdapter",
    "OpenSTEFGBLinearPVForecastAdapter",
    "PVSystemConfig",
    "ghi_to_pv_linear",
]
