"""
OpenSTEF PV forecast adapter — weather-aware inference via MLFlowStorage (infrastructure layer).

Implements two modes per discussion:
1. Direct PV forecast: openSTEF GBLinear trained on pv + weather (end-to-end)
2. Two-stage: irradiance forecast + deterministic PV physics (linear/pvlib)

Model reuse is via the same MLFlowStorage used in training (pv_forecast_openSTEF.ipynb).
on_predict_start of MLFlowStorageCallback (mlflow_storage_callback.py:88) will load
the latest run if model is not fitted, so adapter just re-creates workflow with same model_id.

This adapter exposes a simple domain interface for microgrid simulation:
  - predict_pv_quantiles(dataset, forecast_start) -> ForecastDataset
  - forecast_pv_kw(at: Timestamp) -> float  (P50 point forecast for controller)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

import pandas as pd

from openstef_core.datasets import TimeSeriesDataset
from openstef_core.datasets.validated_datasets import ForecastDataset

from smart_grid_lab.infrastructure.forecasting.pv_physics import PVSystemConfig


class OpenSTEFGBLinearPVForecastAdapter:
    """Adapter for PV forecasting with MLFlow persistence.

    Wraps a ForecastingWorkflowConfig + MLFlowStorage to provide
    reusable inference without re-training.
    """

    def __init__(
        self,
        mlflow_storage,  # MLFlowStorage instance (same tracking_uri as training)
        model_id: str = "pv_gblinear",
        pv_config: PVSystemConfig | None = None,
        two_stage: bool = False,
        # inference-time defaults matching training config
        radiation_column: str = "shortwave_radiation",
        temperature_column: str = "temperature_2m",
    ) -> None:
        from openstef_models.integrations.mlflow import MLFlowStorage

        if not isinstance(mlflow_storage, MLFlowStorage):
            raise TypeError("mlflow_storage must be MLFlowStorage instance")
        self.storage = mlflow_storage
        self.model_id = model_id
        self.pv_config = pv_config or PVSystemConfig()
        self.two_stage = two_stage
        self.radiation_column = radiation_column
        self.temperature_column = temperature_column
        self._workflow = None  # lazy

    def _get_workflow(self):
        """Recreate workflow with same model_id + storage (triggers MLFlowStorageCallback load on predict)."""
        if self._workflow is not None:
            return self._workflow
        from pydantic_extra_types.coordinate import Coordinate, Latitude, Longitude
        from decimal import Decimal
        from openstef_core.types import LeadTime, Q
        from openstef_models.presets import ForecastingWorkflowConfig, create_forecasting_workflow
        from openstef_models.presets.forecasting_workflow import GBLinearForecaster, LocationConfig

        # For two-stage, target is radiation, else pv
        target = self.radiation_column if self.two_stage else "pv"
        config = ForecastingWorkflowConfig(
            model_id=self.model_id if not self.two_stage else f"{self.model_id}_ghi",
            model="gblinear",
            horizons=[LeadTime.from_string("PT36H")],
            quantiles=[Q(0.1), Q(0.5), Q(0.9)],
            target_column=target,
            radiation_column=self.radiation_column,
            temperature_column=self.temperature_column,
            relative_humidity_column="relative_humidity_2m",
            wind_speed_column="wind_speed_10m",
            pressure_column="surface_pressure",
            location=LocationConfig(
                coordinate=Coordinate(latitude=Latitude(Decimal("52.132633")), longitude=Longitude(Decimal("5.291266")))
            ),
            verbosity=0,
            mlflow_storage=self.storage,
            gblinear_hyperparams=GBLinearForecaster.HyperParams(n_steps=50),
        )
        self._workflow = create_forecasting_workflow(config)
        return self._workflow

    def predict_quantiles(
        self,
        dataset: TimeSeriesDataset,
        forecast_start: datetime,
    ) -> ForecastDataset:
        """Return probabilistic forecast (quantiles) for PV or GHI."""
        wf = self._get_workflow()
        forecast: ForecastDataset = wf.predict(dataset, forecast_start=forecast_start)
        if self.two_stage:
            # forecast is GHI quantiles -> convert to PV via physics
            from smart_grid_lab.infrastructure.forecasting.pv_physics import apply_pv_physics_to_forecast

            df = forecast.data
            # try to get temperature from dataset for temp derating
            # forecast.data may not contain temperature; use dataset last temp if needed (approx)
            converted = apply_pv_physics_to_forecast(df, self.pv_config, ghi_column=self.radiation_column, temperature_column=None)
            # wrap back as ForecastDataset (reuse index/sample_interval)
            return ForecastDataset(converted, sample_interval=forecast.sample_interval)
        return forecast

    def forecast_pv_kw(self, dataset: TimeSeriesDataset, at: pd.Timestamp, q: float = 0.5) -> float:
        """Point forecast for controller (P50). Requires dataset to contain history up to `at`."""
        # Use at as forecast_start
        fc = self.predict_quantiles(dataset, forecast_start=at.to_pydatetime())
        # pick quantile closest to q
        col = f"quantile_P{int(q*100)}"
        if col not in fc.data.columns:
            # fallback to first quantile
            col = [c for c in fc.data.columns if c.startswith("quantile_")][0]
        # forecast horizon: first row after `at`
        if at in fc.data.index:
            return float(fc.data.loc[at, col])
        # next valid timestamp
        future = fc.data.index[fc.data.index > at]
        if len(future) == 0:
            raise ValueError(f"No forecast beyond {at}")
        return float(fc.data.loc[future[0], col])

    def load_latest_model_direct(self):
        """Direct storage load without workflow (for debugging)."""
        runs = self.storage.search_latest_runs(self.model_id if not self.two_stage else f"{self.model_id}_ghi")
        if not runs:
            raise FileNotFoundError(f"No MLflow run for {self.model_id}")
        run_id = runs[0].info.run_id
        return self.storage.load_run_model(run_id=run_id, model_id=self.model_id)


# Backwards compat alias for old import
OpenSTEFGBLinearLoadForecastAdapterPV = OpenSTEFGBLinearPVForecastAdapter
