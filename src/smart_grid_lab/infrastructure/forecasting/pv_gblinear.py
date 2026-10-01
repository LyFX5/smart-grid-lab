from pandas import (
    Series,
    Timestamp,
    Timedelta,
)

from smart_grid_lab.core.forecasting import PVForecastModel
from .openstef_adapter import OpenSTEFAdapter


class OpenSTEFGBLinearPVForecastAdapter(PVForecastModel):
    """Adapter for PV forecasting."""

    def __init__(self) -> None:

        self.model_id = "pv_gblinear"
        self.target_column_name = "pv"
        self.openstef_adapter = OpenSTEFAdapter(
            model_id=self.model_id,
            target_column_name=self.target_column_name,
            sample_interval=Timedelta(15, "min"),
        )

    def forecast_pv_kW(
        self,
        history: Series,
        at: Timestamp,
        horizon: Timedelta,
    ) -> Series:
        return self.openstef_adapter.forecast(history, at, horizon, q=0.5)
