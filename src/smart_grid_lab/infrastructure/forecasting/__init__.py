"""Forecast adapters backed by external inference (infrastructure layer)."""

from smart_grid_lab.infrastructure.forecasting.openstef_pv_adapter import (
    OpenSTEFGBLinearPVForecastAdapter,
)
from smart_grid_lab.infrastructure.forecasting.pv_physics import (
    PVSystemConfig,
    ghi_to_pv_linear,
)
from smart_grid_lab.infrastructure.forecasting.sklearn_surplus_adapter import (
    SklearnSurplusForecastAdapter,
)
from smart_grid_lab.infrastructure.forecasting.stef_gblinear_load_adapter import (
    OpenSTEFGBLinearLoadForecastAdapter,
)

__all__ = [
    "SklearnSurplusForecastAdapter",
    "OpenSTEFGBLinearLoadForecastAdapter",
    "OpenSTEFGBLinearPVForecastAdapter",
    "PVSystemConfig",
    "ghi_to_pv_linear",
]
