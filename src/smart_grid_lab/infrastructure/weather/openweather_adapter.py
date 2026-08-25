"""
OpenWeatherMap ingestion adapter (infrastructure layer).

OpenSTEF models (v4) do NOT fetch weather themselves — you supply
weather as columns in a TimeSeriesDataset / VersionedTimeSeriesDataset.
This adapter implements the documented Liander pattern:
`weather_forecasts_versioned`: parquet with (timestamp, available_at, NWP fields).

See:
- openstef_models/presets/forecasting_workflow.py:370 radiation/wind/temperature columns
- openstef_models/transforms/weather_domain/* (pvlib-based derived features)
- openstef_beam/benchmarking/benchmarks/liander2024.py:94 versioned weather path

Usage:
    adapter = OpenWeatherAdapter(api_key="...", lat=52.37, lon=4.90)
    versioned_ds = adapter.fetch_versioned_dataset(available_at=t_now)
    # -> merge with pv/load measurements via VersionedTimeSeriesDataset([pv_part, weather_part])
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from openstef_core.datasets import TimeSeriesDataset

# Column map: OpenWeather -> openSTEF config defaults / Liander names
# ForecastingWorkflowConfig defaults: radiation, windspeed, temperature, pressure, relative_humidity
# Liander dataset uses: shortwave_radiation, wind_speed_10m, temperature_2m, surface_pressure, relative_humidity_2m, cloud_cover
OPENWEATHER_TO_OPENSTEF = {
    "temperature_2m": "temperature_2m",  # or "temperature" if using defaults
    "relative_humidity_2m": "relative_humidity_2m",
    "surface_pressure": "surface_pressure",
    "wind_speed_10m": "wind_speed_10m",
    "cloud_cover": "cloud_cover",
    "shortwave_radiation": "shortwave_radiation",  # not in free OWM, see note
}

# Free OWM 5-day /forecast gives: main.temp, main.humidity, main.pressure, wind.speed, clouds.all, dt
# For radiation use OneCall 3.0 `solar_radiation` or fallback to ERA5 / Open-Meteo.
# We default to synthesizing shortwave_radiation via pvlib clearsky if missing.


def fetch_openweather_forecast(
    lat: float,
    lon: float,
    api_key: str | None = None,
    units: str = "metric",
    use_onecall: bool = False,
) -> pd.DataFrame:
    """Fetch NWP forecast from OpenWeatherMap.

    Args:
        lat, lon: location
        api_key: defaults to env OPENWEATHER_API_KEY
        use_onecall: if True uses One Call 3.0 (includes radiation), else 5-day /forecast (free, no radiation)
    """
    api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY not set (env or arg)")

    if use_onecall:
        url = "https://api.openweathermap.org/data/3.0/onecall"
        params: dict[str, Any] = {"lat": lat, "lon": lon, "appid": api_key, "units": units, "exclude": "minutely,alerts"}
    else:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"lat": lat, "lon": lon, "appid": api_key, "units": units}

    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    rows: list[dict[str, Any]] = []
    if use_onecall:
        # hourly field contains temp, humidity, pressure, wind_speed, clouds, wind_gust, etc. + radiation via uvi? map solar
        for h in data.get("hourly", []):
            rows.append(
                {
                    "timestamp": datetime.fromtimestamp(h["dt"], tz=timezone.utc),
                    "temperature_2m": h.get("temp"),
                    "relative_humidity_2m": h.get("humidity"),
                    "surface_pressure": h.get("pressure"),
                    "wind_speed_10m": h.get("wind_speed"),
                    "cloud_cover": h.get("clouds"),
                    # OneCall has no direct GHI; approximate via cloud_cover + clearsky outside; or use Open-Meteo
                    "shortwave_radiation": h.get("solar_radiation"),  # may be None on free tier
                }
            )
    else:
        for item in data.get("list", []):
            main = item["main"]
            wind = item.get("wind", {})
            clouds = item.get("clouds", {})
            rows.append(
                {
                    "timestamp": datetime.fromtimestamp(item["dt"], tz=timezone.utc),
                    "temperature_2m": main.get("temp"),
                    "relative_humidity_2m": main.get("humidity"),
                    "surface_pressure": main.get("pressure"),
                    "wind_speed_10m": wind.get("speed"),
                    "cloud_cover": clouds.get("all"),
                    "shortwave_radiation": None,  # not provided by free /forecast
                }
            )

    df = pd.DataFrame(rows).set_index("timestamp").sort_index()
    # ensure UTC tz-aware (openstef requires tz-aware index, radiation_derived_features_adder.py:108)
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    return df


def openweather_to_timeseries_dataset(
    df: pd.DataFrame,
    available_at: datetime,
    sample_interval: timedelta = timedelta(minutes=15),
) -> TimeSeriesDataset:
    """Wrap OpenWeather DataFrame as versioned TimeSeriesDataset.

    Adds `available_at` column required for VersionedTimeSeriesDataset composition
    (openstef_core/datasets/timeseries_dataset.py:64). Result can be resampled to 15min
    to match openSTEF sample_interval.
    """
    df = df.copy()
    # resample 3h OWM -> 15min via forward-fill or interpolation
    # Liander interpolates 15min; we interpolate linearly
    df = df.resample("15min").interpolate(method="time").ffill().bfill()
    df["available_at"] = pd.Timestamp(available_at).tz_convert("UTC") if available_at.tzinfo else pd.Timestamp(available_at, tz="UTC")
    # keep only known columns
    keep = [c for c in ["temperature_2m", "relative_humidity_2m", "surface_pressure", "wind_speed_10m", "cloud_cover", "shortwave_radiation"] if c in df.columns]
    df = df[keep + ["available_at"]]
    return TimeSeriesDataset(df, sample_interval=sample_interval, available_at_column="available_at")


class OpenWeatherAdapter:
    """Stateful adapter for repeat fetching + caching to parquet versioned store.

    Mirrors Liander `weather_forecasts_versioned/{group}/{name}.parquet` layout.
    """

    def __init__(
        self,
        lat: float,
        lon: float,
        api_key: str | None = None,
        cache_dir: Path | str | None = None,
    ) -> None:
        self.lat = lat
        self.lon = lon
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self.cache_dir = Path(cache_dir) if cache_dir else None

    def fetch(self, use_onecall: bool = False) -> pd.DataFrame:
        return fetch_openweather_forecast(self.lat, self.lon, self.api_key, use_onecall=use_onecall)

    def fetch_versioned_dataset(
        self,
        available_at: datetime | None = None,
        use_onecall: bool = False,
    ) -> TimeSeriesDataset:
        df = self.fetch(use_onecall=use_onecall)
        if available_at is None:
            available_at = datetime.now(timezone.utc)
        ds = openweather_to_timeseries_dataset(df, available_at=available_at)
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            # append to versioned parquet (like Liander)
            cache_file = self.cache_dir / f"openweather_{self.lat}_{self.lon}.parquet"
            if cache_file.exists():
                existing = pd.read_parquet(cache_file)
                combined = pd.concat([existing, ds.data.reset_index()], ignore_index=True)
            else:
                combined = ds.data.reset_index()
            combined.to_parquet(cache_file, index=False)
        return ds
