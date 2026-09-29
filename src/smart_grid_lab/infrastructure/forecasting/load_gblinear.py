"""
OpenSTEF Load forecast adapter — weather-aware inference via MLFlowStorage (infrastructure layer).
"""

from pandas import (
    Series,
    Timestamp,
    Timedelta,
    DatetimeIndex,
)

from openstef_models.integrations.mlflow import MLFlowStorage

from openstef_core.types import LeadTime, Q
from openstef_models.presets import (
    ForecastingWorkflowConfig,
)
from openstef_models.presets.forecasting_workflow import (
    GBLinearForecaster,
    LocationConfig,
)

from smart_grid_lab.core.forecasting import LoadForecastModel
from smart_grid_lab.domain.microgrid_configuration import MICROGRID_LOCATION

import os

os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"

from pathlib import Path

my_mlflow_storage = MLFlowStorage(
    tracking_uri="./mlflow",  # -> file:///abs/path/mlflow via normalize_tracking_uri
    local_artifacts_path=Path("./mlflow_artifacts_local"),
    # For production DB backend use:
    # tracking_uri="sqlite:///mlflow.db",
    # artifact_location="file:///tmp/mlflow_artifacts",
)
# TODO separate mlflowstarage for load  ?


from .openstef_adapter import OpenSTEFAdapter


class OpenSTEFGBLinearLoadForecastAdapter(LoadForecastModel):
    """Adapter for Load forecasting.

    Wraps a ForecastingWorkflowConfig + MLFlowStorage to provide
    reusable inference without re-training.
    """

    def __init__(
        self,
        mlflow_storage: MLFlowStorage = my_mlflow_storage,  # MLFlowStorage instance (same tracking_uri as training)
    ) -> None:

        if not isinstance(mlflow_storage, MLFlowStorage):
            raise TypeError("mlflow_storage must be MLFlowStorage instance")

        self.storage = mlflow_storage
        self.model_id = "load_gblinear"
        self.load_column_name = "load"

        self.config = ForecastingWorkflowConfig(
            model_id=self.model_id,
            model="gblinear",
            horizons=[LeadTime.from_string("PT36H")],
            quantiles=[Q(0.1), Q(0.5), Q(0.9)],
            target_column=self.load_column_name,
            radiation_column="shortwave_radiation",
            temperature_column="temperature_2m",
            relative_humidity_column="relative_humidity_2m",
            wind_speed_column="wind_speed_10m",
            pressure_column="surface_pressure",
            location=LocationConfig(coordinate=MICROGRID_LOCATION),
            verbosity=0,
            mlflow_storage=self.storage,
            gblinear_hyperparams=GBLinearForecaster.HyperParams(n_steps=50),
        )

        self.openstef_adapter = OpenSTEFAdapter(
            config=self.config,
            target_column_name=self.load_column_name,
            sample_interval=Timedelta(15, "min"),
            index_name="datetime",
            index_type=DatetimeIndex,
        )

    def forecast_pv_kW(
        self,
        history: Series,
        at: Timestamp,
        horizon: Timedelta,
    ) -> Series:
        return self.openstef_adapter.forecast(history, at, horizon, q=0.5)
