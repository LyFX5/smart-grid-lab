"""Load forecast adapter — weather-aware inference via MLFlowStorage.

Keeps the old `model_path` fallback for backwards compat, but primary
reuse is via MLFlowStorage (same tracking_uri/model_id as training).
See OpenSTEFGBLinearPVForecastAdapter for PV-specific physics.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from smart_grid_lab.core.forecasting import LoadForecastModel


class OpenSTEFGBLinearLoadForecastAdapter(LoadForecastModel):
    def __init__(
        self,
        model_path: Optional[str] = None,
        mlflow_storage=None,  # MLFlowStorage
        model_id: str = "load_gblinear",
    ) -> None:
        self._model_path = Path(model_path) if model_path else None
        self._mlflow_storage = mlflow_storage
        self._model_id = model_id
        self._workflow = None

    def _get_workflow(self):
        if self._workflow is not None:
            return self._workflow
        if self._mlflow_storage is None:
            return None
        from pydantic_extra_types.coordinate import Coordinate, Latitude, Longitude
        from decimal import Decimal
        from openstef_core.types import LeadTime, Q
        from openstef_models.presets import ForecastingWorkflowConfig, create_forecasting_workflow
        from openstef_models.presets.forecasting_workflow import GBLinearForecaster, LocationConfig

        config = ForecastingWorkflowConfig(
            model_id=self._model_id,
            model="gblinear",
            horizons=[LeadTime.from_string("PT36H")],
            quantiles=[Q(0.1), Q(0.5), Q(0.9)],
            target_column="load",
            radiation_column="radiation",
            wind_speed_column="windspeed",
            temperature_column="temperature",
            pressure_column="pressure",
            relative_humidity_column="relative_humidity",
            location=LocationConfig(
                coordinate=Coordinate(latitude=Latitude(Decimal("52.132633")), longitude=Longitude(Decimal("5.291266")))
            ),
            verbosity=0,
            mlflow_storage=self._mlflow_storage,
            gblinear_hyperparams=GBLinearForecaster.HyperParams(n_steps=50),
        )
        self._workflow = create_forecasting_workflow(config)
        return self._workflow

    def forecast_load_kW(self, history: pd.Series, at: pd.Timestamp) -> float:
        # MLFlow path: delegate to workflow.predict if storage provided
        wf = self._get_workflow()
        if wf is not None:
            # Build minimal dataset from history (requires lags)
            from openstef_core.datasets import TimeSeriesDataset
            from datetime import timedelta

            df = pd.DataFrame({"load": history})
            df.index = pd.to_datetime(df.index, utc=True)
            ds = TimeSeriesDataset(df, sample_interval=timedelta(minutes=15))
            try:
                fc = wf.predict(ds, forecast_start=at.to_pydatetime())
                col = "quantile_P50" if "quantile_P50" in fc.data.columns else [c for c in fc.data.columns if c.startswith("quantile_")][0]
                future = fc.data.index[fc.data.index >= at]
                if len(future):
                    return float(fc.data.loc[future[0], col])
            except Exception:
                pass  # fallback to persistence
        if self._model_path is None:
            return float(history.loc[at])
        raise NotImplementedError(
            "OpenSTEFGBLinearLoadForecastAdapter: wire model load + predict mapping "
            f"for path {self._model_path!r}."
        )
