import numpy as np
from pandas import (
    DataFrame,
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


def get_dynamic_import_price(
    timestamp: Timestamp, base_price: float = 40.0
) -> float:

    fixed_component = 15.0  # ct/kWh (grid fees, taxes, baseline procurement)
    dynamic_range = base_price - fixed_component  # e.g., 25.0 ct/kWh

    multiplier = get_smooth_dynamic_multiplier(timestamp)
    return fixed_component + (dynamic_range * multiplier)


def get_dynamic_export_price(
    timestamp: Timestamp,  # base_export_price: float = 8.5
) -> float:
    """
    Calculates the dynamic export (feed-in) price in ct/kWh.
    Tracks wholesale market dynamics: low/negative during midday solar peaks,
    higher during evening demand peaks.
    """
    hour_decimal = timestamp.hour + timestamp.minute / 60.0

    # Wholesale base average (simplified)
    wholesale_base = 6.0

    # Midday solar surplus (drives wholesale price down, can go slightly negative)
    solar_surplus = -4.0 * np.exp(-((hour_decimal - 13.0) ** 2) / (2 * 3.5**2))

    # Evening demand peak (drives wholesale price up)
    evening_premium = 3.0 * np.exp(
        -((hour_decimal - 19.0) ** 2) / (2 * 2.5**2)
    )

    raw_export_price = wholesale_base + solar_surplus + evening_premium

    # If simulating a fixed EEG feed-in tariff, you would just return `base_feed_in`.
    # If simulating dynamic market participation, return the calculated wholesale price.
    # We cap the minimum at 0.0 for simplicity, unless you specifically want to model negative prices.
    return float(np.clip(raw_export_price, 0.0, 15.0))


def generate_smooth_tariff_series(
    start: Timestamp,
    end: Timestamp,
    sample_interval: Timedelta,
    base_import_price: float = 40.0,
    base_export_price: float = 8.5,
) -> DataFrame:

    start_ts = to_datetime(start)
    end_ts = to_datetime(end)
    freq = to_timedelta(sample_interval)

    idx = date_range(start=start_ts, end=end_ts, freq=freq)
    import_prices = [
        get_dynamic_import_price(ts, base_price=base_import_price)
        for ts in idx
    ]
    export_prices = [get_dynamic_export_price(ts) for ts in idx]

    return DataFrame(
        data={
            "import_price_ct_per_kwh": import_prices,
            "export_price_ct_per_kwh": export_prices,
        },
        index=idx,
    )


# Example Usage
tariff_march_2016 = generate_smooth_tariff_series(
    start=Timestamp(year=2016, month=3, day=15, hour=12, tz="utc"),
    end=Timestamp(year=2016, month=3, day=30, hour=12, tz="utc"),
    sample_interval=Timedelta(15, "min"),
)
