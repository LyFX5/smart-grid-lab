"""
preparing data
(https://data.open-power-system-data.org/household_data/2020-04-15)
for experiment "offgrid h2 forecast-based control"
"""

import numpy as np
import pandas as pd


def raw_data_path():
    folder = "data/raw/"
    file = "household_data_15min_singleindex.csv"
    return folder + file


def load_raw(path) -> pd.DataFrame:
    return pd.read_csv(path)


def categorize_columns(raw_data) -> ...:
    all_cols = raw_data.columns.tolist()

    pv_cols = [c for c in all_cols if "_pv" in c]

    battery_cols = [
        c
        for c in all_cols
        if "storage_charge" in c or "storage_decharge" in c or "battery" in c
    ]

    grid_cols = [
        c for c in all_cols if "grid_import" in c or "grid_export" in c
    ]

    exclude = (
        pv_cols
        + battery_cols
        + grid_cols
        + ["utc_timestamp", "cet_cest_timestamp", "interpolated"]
    )

    load_cols = [c for c in all_cols if c not in exclude]

    return (pv_cols, load_cols, battery_cols, grid_cols)


def compact_table(raw_data):
    pv_cols, load_cols, battery_cols, grid_cols = categorize_columns(raw_data)

    # category tables
    """
    df_load = raw_data[["utc_timestamp"] + load_cols]
    df_pv = raw_data[["utc_timestamp"] + pv_cols]
    df_grid = raw_data[["utc_timestamp"] + grid_cols]
    df_battery = raw_data[["utc_timestamp"] + battery_cols]
    """

    # energy table
    energy_df = pd.DataFrame(
        {
            "utc_timestamp": raw_data["utc_timestamp"],
            # total demand / consumption
            "load": raw_data[load_cols].sum(axis=1),
            # total PV generation
            "pv": raw_data[pv_cols].sum(axis=1),
            # net grid exchange
            # import positive, export negative
            "grid": (
                raw_data[[c for c in grid_cols if "import" in c]].sum(axis=1)
                - raw_data[[c for c in grid_cols if "export" in c]].sum(axis=1)
            ),
            # battery net power
            # charge negative, discharge positive
            "battery": (
                raw_data[[c for c in battery_cols if "decharge" in c]].sum(
                    axis=1
                )
                - raw_data[[c for c in battery_cols if "charge" in c]].sum(
                    axis=1
                )
            ),
        }
    )

    energy_df["utc_timestamp"] = pd.to_datetime(
        energy_df["utc_timestamp"],
        utc=True,
    )

    energy_df = energy_df.set_index("utc_timestamp")

    power_df = energy_df.diff()

    # some preprocessing (clear anomal values (negative production / consumption))
    power_df[["load", "pv"]] = power_df[["load", "pv"]].clip(lower=0)

    return power_df


"""
def column(power_df, name):
    column_df = power_df[[name]]
    column_df.index = pd.to_datetime(column_df.index, utc=True)
    column_df = column_df.sort_index()
    column_df = column_df.asfreq("15min")
    return column_df
"""


def append_time_features(df: pd.DataFrame, target: str):
    df = df.copy()

    df["hour"] = df.index.hour
    df["dayofweek"] = df.index.dayofweek
    df["month"] = df.index.month
    df["dayofyear"] = df.index.dayofyear
    df["weekofyear"] = df.index.isocalendar().week.astype(int)

    df["is_weekend"] = (df["dayofweek"] >= 5).astype(int)

    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)

    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

    df["dow_sin"] = np.sin(2 * np.pi * df["dayofweek"] / 7)

    df["dow_cos"] = np.cos(2 * np.pi * df["dayofweek"] / 7)

    df["load_lag_1h"] = df[target].shift(4)

    df["load_lag_6h"] = df[target].shift(24)

    df["load_lag_24h"] = df[target].shift(96)

    df["load_lag_48h"] = df[target].shift(192)

    df["load_lag_7d"] = df[target].shift(96 * 7)

    df["load_roll_mean_24h"] = df[target].shift(1).rolling(96).mean()

    df["load_roll_std_24h"] = df[target].shift(1).rolling(96).std()

    df = df.dropna()

    return df


"""
def save_prepared():
    # save by separate series
    # and tables (like features table)
    # probably training / test tables
    # and stef-ready table will be prepared in infra
    # in data folder
    ...


if __name__ == "__main__":
    save_prepared()
"""
