import pandas as pd
from numpy import nan as np_nan
from sklearn.ensemble import IsolationForest


def remove_outliers_iforest(
    df: pd.DataFrame, value_col="pv", contamination=0.001
) -> pd.DataFrame:
    # features: value + simple time context
    X = df[[value_col]].copy()
    X["hour"] = df.index.hour
    X["rolling_mean_24h"] = df[value_col].rolling(24, min_periods=1).mean()

    X = X.fillna(0)
    iso = IsolationForest(
        contamination=contamination,  # tune: fraction of expected anomalies
        random_state=42,
    )
    df["is_anomaly"] = iso.fit_predict(X) == -1

    # option A: drop, option B: mask as NaN (better — OpenSTEF handles NaNs)
    df.loc[df["is_anomaly"], value_col] = np_nan
    return df


from sklearn.linear_model import HuberRegressor


def flag_contextual_outliers(df, value_col="pv", window=96, threshold=5.0):
    med = df[value_col].rolling(window, center=True, min_periods=1).median()
    mad = (
        (df[value_col] - med)
        .abs()
        .rolling(window, center=True, min_periods=1)
        .median()
    )
    # robust z-score (MAD-based)
    robust_z = 0.6745 * (df[value_col] - med) / mad.replace(0, np_nan)
    df.loc[robust_z.abs() > threshold, value_col] = np_nan
    return df


def pv_constraint(df, pv_peak_kW, interpolate=False):

    # Physical constraint + clear-sky envelope
    # hard capacity limit
    df.loc[df["pv"] > pv_peak_kW * 1.1, "pv"] = np_nan  # impossible generation
    df.loc[df["pv"] < 0, "pv"] = np_nan  # negative generation

    # clear-sky envelope: generation must be 0 (or near 0) at night
    night = (df.index.hour < 5) | (df.index.hour > 22)
    df.loc[night & (df["pv"] > 0.05 * df["pv"].quantile(0.99)), "pv"] = np_nan

    if interpolate:
        df["pv"] = df["pv"].interpolate(method="time", limit=4)

    return df
