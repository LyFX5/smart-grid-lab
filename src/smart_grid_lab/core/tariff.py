import numpy as np
from pandas import (
    Series,
    Timestamp,
    Timedelta,
    date_range,
    to_datetime,
    to_timedelta,
)


def get_smooth_dynamic_multiplier(timestamp: Timestamp) -> float:
    """
    Generates a smooth, differentiable price multiplier (0.0 to 1.0)
    based on continuous time, with distinct profiles for weekdays and weekends.
    """
    hour_decimal = timestamp.hour + timestamp.minute / 60.0
    is_weekend = timestamp.dayofweek >= 5  # 5 = Saturday, 6 = Sunday

    # 1. Base load (lower on weekends due to industrial/commercial shutdown)
    base = 0.2 if is_weekend else 0.3

    # 2. Evening peak (shifts later and shrinks slightly on weekends)
    evening_center = 20.0 if is_weekend else 19.0
    evening_amplitude = 0.6 if is_weekend else 0.7
    evening_width = 2.5
    evening_peak = evening_amplitude * np.exp(
        -((hour_decimal - evening_center) ** 2) / (2 * evening_width**2)
    )

    # 3. Morning peak (shifts later and shrinks significantly on weekends)
    morning_center = 10.0 if is_weekend else 8.0
    morning_amplitude = 0.1 if is_weekend else 0.25
    morning_width = 2.0
    morning_peak = morning_amplitude * np.exp(
        -((hour_decimal - morning_center) ** 2) / (2 * morning_width**2)
    )

    # 4. Midday solar dip (deeper relatively on weekends due to lower baseline demand)
    solar_dip_amplitude = -0.15 if is_weekend else -0.2
    solar_width = 3.5
    solar_dip = solar_dip_amplitude * np.exp(
        -((hour_decimal - 13.0) ** 2) / (2 * solar_width**2)
    )

    raw_multiplier = base + evening_peak + morning_peak + solar_dip

    # Global normalization to ensure consistent absolute pricing across the week
    # Empirical global min ~0.05, global max ~1.0
    normalized = (raw_multiplier - 0.05) / 0.95
    return float(np.clip(normalized, 0.0, 1.0))


def calculate_realistic_tariff(
    timestamp: Timestamp, base_price: float = 40.0
) -> float:
    """
    Calculates a realistic price in ct/kWh for a given timestamp.
    Splits the base price into fixed grid/tax costs and dynamic wholesale exposure.
    """
    fixed_component = 15.0  # ct/kWh (grid fees, taxes, baseline procurement)
    dynamic_range = base_price - fixed_component  # e.g., 25.0 ct/kWh

    multiplier = get_smooth_dynamic_multiplier(timestamp)
    return fixed_component + (dynamic_range * multiplier)


def generate_smooth_tariff_series(
    start: Timestamp,
    end: Timestamp,
    sample_interval: Timedelta,
    base_price: float = 40.0,
) -> Series:
    """
    Generates a smooth, realistic price series in ct/kWh for an arbitrary time range,
    automatically adapting to weekday/weekend patterns.
    """
    start_ts = to_datetime(start)
    end_ts = to_datetime(end)
    freq = to_timedelta(sample_interval)

    idx = date_range(start=start_ts, end=end_ts, freq=freq)
    prices = [
        calculate_realistic_tariff(ts, base_price=base_price) for ts in idx
    ]

    return Series(prices, index=idx, name="price_ct_per_kwh")


# Example Usage
tariff_march_2016 = generate_smooth_tariff_series(
    start=Timestamp(year=2016, month=3, day=15, hour=12, tz="utc"),
    end=Timestamp(year=2016, month=3, day=30, hour=12, tz="utc"),
    sample_interval=Timedelta(15, "min"),
)
