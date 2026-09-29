"""
OpenSTEF forecast adapter — weather-aware inference via MLFlowStorage (infrastructure layer).
"""

from numpy import nan as np_nan
from pandas import (
    DataFrame,
    Series,
    Timestamp,
    Timedelta,
    DatetimeIndex,
    merge,
    date_range,
    concat,
)

from datetime import datetime

from openstef_core.datasets import TimeSeriesDataset
from openstef_core.datasets.validated_datasets import ForecastDataset

from openstef_models.presets import (
    ForecastingWorkflowConfig,
)
from openstef_models.presets import (
    create_forecasting_workflow,
)

from smart_grid_lab.domain.microgrid_configuration import MICROGRID_LOCATION

from smart_grid_lab.infrastructure.weather.openmeteo_adapter import (
    OpenMeteoAdapter,
)


class OpenSTEFAdapter:

    def __init__(
        self,
        config: ForecastingWorkflowConfig,
        target_column_name: str,
        sample_interval: Timedelta,
        index_name: str,
        index_type: DatetimeIndex,
    ) -> None:

        self.config = config
        self.target_column_name = target_column_name
        self.sample_interval = sample_interval
        self.index_name = index_name
        self.index_type = index_type
        self._workflow = None

    def _get_workflow(self):
        """Recreate workflow with same model_id + storage (triggers MLFlowStorageCallback load on predict)."""
        if self._workflow is not None:
            return self._workflow
        self._workflow = create_forecasting_workflow(self.config)
        return self._workflow

    def predict_quantiles(
        self,
        dataset: TimeSeriesDataset,
        forecast_start: datetime | Timestamp,
    ) -> ForecastDataset:
        """Return probabilistic forecast (quantiles)"""
        wf = self._get_workflow()
        forecast: ForecastDataset = wf.predict(
            dataset, forecast_start=forecast_start
        )
        return forecast

    def validate(self, timeseries: Series | DataFrame) -> DataFrame:

        if not isinstance(timeseries.index, self.index_type):
            raise TypeError(
                f"timeseries index type must be: {self.index_type}"
            )

        if not isinstance(timeseries, DataFrame):
            timeseries = timeseries.to_frame()

        if timeseries.columns[0] is not self.target_column_name:
            timeseries = timeseries.rename(
                columns={timeseries.columns[0]: self.target_column_name}
            )

        if timeseries.index.name is not self.index_name:
            timeseries.index.name = self.index_name

        return timeseries

    def merge_weather_features(self, df: DataFrame) -> DataFrame:

        open_meteo = OpenMeteoAdapter(
            MICROGRID_LOCATION.latitude, MICROGRID_LOCATION.longitude
        )
        weather_df = open_meteo.historical(
            start_date=df.index[0], end_date=df.index[-1]
        )
        weather_df = (
            weather_df.resample(self.sample_interval)
            .interpolate(method="time")
            .ffill()
            .bfill()
        )
        return merge(
            df,
            weather_df,
            left_index=True,
            right_index=True,
            how="left",
        )

    def to_dataset(self, df: DataFrame) -> TimeSeriesDataset:
        return TimeSeriesDataset(df, sample_interval=self.sample_interval)

    def train(self, train_df: DataFrame) -> None:

        train_df = self.validate(train_df)
        train_df = self.merge_weather_features(train_df)
        train_dataset = self.to_dataset(train_df)

        wf = self._get_workflow()

        result = wf.fit(train_dataset)
        if result is not None:
            print("Training metrics:")
            print(result.metrics_full.to_dataframe())
            if result.metrics_test is not None:
                print("\nTest metrics:")
                print(result.metrics_test.to_dataframe())
        else:
            print("Fit skipped (model reuse, recent enough)")

    def test(self, test_df: DataFrame, at: Timestamp) -> ForecastDataset:

        test_df = self.validate(test_df)
        test_df = self.merge_weather_features(test_df)
        test_dataset = self.to_dataset(test_df)

        return self.predict_quantiles(test_dataset, at)

    def placeholder_for_forecast_data(
        self, at: Timestamp, horizon: Timedelta
    ) -> Series:
        num_intervals = int(horizon / self.sample_interval)
        index = date_range(
            start=at,
            end=at + horizon - self.sample_interval,
            freq=self.sample_interval,
            name=self.index_name,
        )
        return Series(
            [np_nan] * num_intervals, index=index, name=self.target_column_name
        )

    def forecast(
        self,
        history: Series,
        at: Timestamp,
        horizon: Timedelta,
        q: float = 0.5,
    ) -> Series:

        assert at == (
            history.index[-1] + self.sample_interval
        ), "forecast must start after history"

        forecast = self.placeholder_for_forecast_data(at, horizon)
        forecast = self.validate(forecast)
        history = self.validate(history)

        forecast = concat([history, forecast])
        forecast = forecast[~forecast.index.duplicated(keep="first")]

        forecast = self.merge_weather_features(
            forecast
        )  # TODO in real time use weather FORECAST API (not historical API)

        forecast = self.to_dataset(forecast)

        forecast = self.predict_quantiles(forecast, at)

        col = f"quantile_P{int(q*100)}"
        if col not in forecast.data.columns:
            # fallback to first quantile
            col = [
                c for c in forecast.data.columns if c.startswith("quantile_")
            ][0]

        return forecast.data[col]

    def postprocess(
        self,
        dataset: TimeSeriesDataset | ForecastDataset,
    ) -> Series: ...
