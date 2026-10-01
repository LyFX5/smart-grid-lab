from pandas import (
    Series,
    Timestamp,
    Timedelta,
)

from smart_grid_lab.core.forecasting import LoadForecastModel
from .openstef_adapter import OpenSTEFAdapter


class OpenSTEFGBLinearLoadForecastAdapter(LoadForecastModel):
    """Adapter for Load forecasting."""

    def __init__(self) -> None:

        self.model_id = "load_gblinear"
        self.target_column_name = "load"
        self.openstef_adapter = OpenSTEFAdapter(
            model_id=self.model_id,
            target_column_name=self.target_column_name,
            sample_interval=Timedelta(15, "min"),
        )

    def forecast_load_kW(
        self,
        history: Series,
        at: Timestamp,
        horizon: Timedelta,
    ) -> Series:
        return self.openstef_adapter.forecast(history, at, horizon, q=0.5)
