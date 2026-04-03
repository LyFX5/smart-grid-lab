from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State
from plotly.subplots import make_subplots

from smart_grid_lab import Time
from smart_grid_lab.application.use_cases.run_simulation import (
    BatteryConfig,
    SimulationSetup,
    TimeConfig,
    run_simulation as run_simulation_use_case,
)


def _time_index_and_periods(time: Time) -> tuple[pd.DatetimeIndex, int]:
    periods = int((time.end - time.start) // time.step)
    time_index = pd.date_range(time.start, periods=periods, freq=time.step)
    return time_index, periods


def _series_to_store(s: pd.Series) -> dict:
    return {
        "index": s.index.astype(str).tolist(),
        "values": s.astype(float).tolist(),
    }


def _series_from_store(data: dict | None) -> pd.Series | None:
    if not data or "index" not in data or "values" not in data:
        return None
    idx = pd.DatetimeIndex(data["index"])
    return pd.Series(data=data["values"], index=idx, dtype=float)


def sample_solar_irradiance(time_index: pd.DatetimeIndex) -> pd.Series:
    hour = time_index.hour
    ghi = np.maximum(0, 800 * np.sin(np.pi * (hour - 6) / 12))
    ghi += np.random.normal(0, 50, len(ghi))
    ghi /= 1000.0
    return pd.Series(data=ghi, index=time_index)


def sample_load_power(time_index: pd.DatetimeIndex, periods: int) -> pd.Series:
    np.random.seed(42)
    base_load = 20 + 10 * np.sin(2 * np.pi * np.arange(periods) / 24)
    load = np.maximum(5, base_load + np.random.normal(0, 3, periods))
    return pd.Series(data=load, index=time_index)


def _empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        title="Microgrid Dynamics",
        annotations=[
            dict(
                text=message,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14),
            )
        ],
    )
    return fig


def make_dynamics_figure(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    left_cols = [
        "solar_power",
        "load_power",
        "battery_available_power",
        "battery_charge_power",
        "battery_discharge_power",
    ]
    right_cols = ["battery_soc"]

    for col in left_cols:
        if col in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df[col], name=col),
                secondary_y=False,
            )

    for col in right_cols:
        if col in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df[col], name=col),
                secondary_y=True,
            )

    fig.update_layout(title="Microgrid Dynamics")
    fig.update_yaxes(title_text="Power (kW)", secondary_y=False)
    fig.update_yaxes(title_text="SOC (%)", secondary_y=True)
    return fig


def _time_from_inputs(
    start: str | None,
    end: str | None,
    step_minutes: int | float | None,
) -> Time:
    """
    Build a core `Time` object from UI inputs, with safe fallbacks.
    """
    if not start:
        start = "2026-03-15 12:00:00"
    if not end:
        end = "2026-03-20 12:00:00"
    try:
        step_val = int(step_minutes) if step_minutes is not None else 10
    except (TypeError, ValueError):
        step_val = 10

    return Time(
        start=pd.Timestamp(start),
        end=pd.Timestamp(end),
        step=pd.Timedelta(step_val, "min"),
    )


def register_simulation_callbacks(app) -> None:

    @app.callback(
        Output("solar-profile-store", "data"),
        Input("btn-solar-sample", "n_clicks"),
        State("time-start", "value"),
        State("time-end", "value"),
        State("time-step-minutes", "value"),
        prevent_initial_call=True,
    )
    def load_solar_sample(_n_clicks, start, end, step_minutes):
        time = _time_from_inputs(start, end, step_minutes)
        ti, _ = _time_index_and_periods(time)
        return _series_to_store(sample_solar_irradiance(ti))

    @app.callback(
        Output("load-profile-store", "data"),
        Input("btn-load-sample", "n_clicks"),
        State("time-start", "value"),
        State("time-end", "value"),
        State("time-step-minutes", "value"),
        prevent_initial_call=True,
    )
    def load_load_sample(_n_clicks, start, end, step_minutes):
        time = _time_from_inputs(start, end, step_minutes)
        ti, periods = _time_index_and_periods(time)
        return _series_to_store(sample_load_power(ti, periods))

    @app.callback(
        Output("main-graph", "figure"),
        Input("btn-run-simulation", "n_clicks"),
        State("solar-profile-store", "data"),
        State("load-profile-store", "data"),
        State("time-start", "value"),
        State("time-end", "value"),
        State("time-step-minutes", "value"),
        State("battery-capacity-kwh", "value"),
        State("battery-max-charge-kw", "value"),
        State("battery-max-discharge-kw", "value"),
        State("battery-charge-efficiency", "value"),
        State("battery-discharge-efficiency", "value"),
        State("battery-initial-soc", "value"),
        prevent_initial_call=True,
    )
    def run_simulation(
        n_clicks,
        solar_data,
        load_data,
        start,
        end,
        step_minutes,
        capacity_kwh,
        max_charge_kw,
        max_discharge_kw,
        charge_eff,
        discharge_eff,
        initial_soc,
    ):
        if not n_clicks:
            return _empty_figure('Click "Run Simulation" to compute results.')

        time = _time_from_inputs(start, end, step_minutes)
        ti, periods = _time_index_and_periods(time)
        solar_series = _series_from_store(solar_data)
        if solar_series is None:
            solar_series = sample_solar_irradiance(ti)

        load_series = _series_from_store(load_data)
        if load_series is None:
            load_series = sample_load_power(ti, periods)

        def _num(v, default):
            if v is None:
                return default
            try:
                return float(v)
            except (TypeError, ValueError):
                return default

        capacity_kwh = _num(capacity_kwh, 100.0)
        max_charge_kw = _num(max_charge_kw, 30.0)
        max_discharge_kw = _num(max_discharge_kw, 30.0)
        charge_eff = _num(charge_eff, 0.95)
        discharge_eff = _num(discharge_eff, 0.95)
        initial_soc = _num(initial_soc, 0.5)

        time_cfg = TimeConfig(
            start=str(time.start),
            end=str(time.end),
            step_minutes=int(time.step / pd.Timedelta(1, "min")),
        )
        battery_cfg = BatteryConfig(
            capacity_kwh=capacity_kwh,
            max_charge_kw=max_charge_kw,
            max_discharge_kw=max_discharge_kw,
            max_charge_efficiency=charge_eff,
            max_discharge_efficiency=discharge_eff,
            initial_soc=initial_soc,
        )
        app_setup = SimulationSetup(
            time=time_cfg,
            battery=battery_cfg,
            solar_profile=solar_series,
            load_profile=load_series,
        )
        df = run_simulation_use_case(app_setup, use_bar=False)
        return make_dynamics_figure(df)
