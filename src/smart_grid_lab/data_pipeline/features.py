import numpy as np
import pandas as pd


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
