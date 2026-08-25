"""
Liander weather adapter — loads versioned NWP as used in benchmarking.

Wraps liander_dataset/weather_forecasts_versioned parquet into
a VersionedTimeSeriesDataset-ready TimeSeriesDataset.

This is the reference implementation for how openSTEF expects weather:
- file has (timestamp, available_at, temperature_2m, shortwave_radiation, ...)
- you filter by available_at at train/predict time (avoids look-ahead)
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pandas as pd

from openstef_core.datasets import TimeSeriesDataset


DEFAULT_WEATHER_PATH = Path("liander_dataset/weather_forecasts_versioned/mv_feeder/OS Gorredijk.parquet")

# Columns present in Liander weather parquet:
# timestamp, available_at, temperature_2m, relative_humidity_2m, surface_pressure,
# cloud_cover, wind_speed_10m, wind_speed_80m, wind_direction_10m,
# shortwave_radiation, direct_radiation, diffuse_radiation, direct_normal_irradiance
LIANDER_RENAME_MAP = {}  # keep as-is; ForecastingWorkflowConfig will be configured to match


def load_liander_weather_dataset(
    path: Path | str = DEFAULT_WEATHER_PATH,
    sample_interval: timedelta = timedelta(minutes=15),
) -> TimeSeriesDataset:
    """Load Liander versioned weather parquet as versioned TimeSeriesDataset.

    Returns a TimeSeriesDataset with available_at_column="available_at"
    so it can be composed: VersionedTimeSeriesDataset([pv_part, weather_part])
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Weather parquet not found: {path.resolve()}. Expected Liander dataset.")

    df = pd.read_parquet(path)
    # ensure dtypes / tz
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["available_at"] = pd.to_datetime(df["available_at"], utc=True)
    df = df.set_index("timestamp").sort_index()
    # keep relevant columns; drop wind_speed_80m etc if not needed but keep all
    return TimeSeriesDataset(df, sample_interval=sample_interval, available_at_column="available_at")
