"""Weather ingestion adapters (infrastructure layer)."""

from smart_grid_lab.infrastructure.weather.openweather_adapter import (
    OpenWeatherAdapter,
    fetch_openweather_forecast,
    openweather_to_timeseries_dataset,
)
from smart_grid_lab.infrastructure.weather.liander_weather_adapter import (
    load_liander_weather_dataset,
)
from smart_grid_lab.infrastructure.weather.openmeteo_adapter import (
    OpenMeteoAdapter,
)

__all__ = [
    "OpenWeatherAdapter",
    "fetch_openweather_forecast",
    "openweather_to_timeseries_dataset",
    "load_liander_weather_dataset",
    "OpenMeteoAdapter",
]
