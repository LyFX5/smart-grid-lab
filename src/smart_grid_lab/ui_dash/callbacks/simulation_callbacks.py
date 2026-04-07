from __future__ import annotations

import numpy as np
import pandas as pd

import plotly.graph_objects as go
from dash import dcc, html
from dash import Input, Output, State
from plotly.subplots import make_subplots

import smart_grid_lab.application.use_cases.base as base_simulation


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


def make_telemetry_figure(df: pd.DataFrame) -> go.Figure:
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


def make_metrics_table(df: pd.DataFrame) -> html.Table:
    return html.Table(
        [
            html.Thead(html.Tr([html.Th(col) for col in df.columns])),
            html.Tbody(
                [
                    html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
                    for i in range(len(df))
                ]
            ),
        ]
    )


def _empty_table():
    make_metrics_table(pd.DataFrame())


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
        time_cfg = base_simulation.time_config_from_inputs(start, end, step_minutes)
        time = base_simulation.build_time(time_cfg)
        return _series_to_store(sample_solar_irradiance(time.index_range))

    @app.callback(
        Output("load-profile-store", "data"),
        Input("btn-load-sample", "n_clicks"),
        State("time-start", "value"),
        State("time-end", "value"),
        State("time-step-minutes", "value"),
        prevent_initial_call=True,
    )
    def load_load_sample(_n_clicks, start, end, step_minutes):
        time_cfg = base_simulation.time_config_from_inputs(start, end, step_minutes)
        time = base_simulation.build_time(time_cfg)
        return _series_to_store(sample_load_power(time.index_range, time.periods))

    @app.callback(
        Output("telemetry-figure", "figure"),
        Output("metrics-table", "children"),
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
            return (
                _empty_figure('Click "Run Simulation" to compute results.'),
                _empty_table(),
            )

        time_cfg = base_simulation.time_config_from_inputs(start, end, step_minutes)
        time = base_simulation.build_time(time_cfg)

        solar_series = _series_from_store(solar_data)
        if solar_series is None:
            solar_series = sample_solar_irradiance(time.index_range)

        load_series = _series_from_store(load_data)
        if load_series is None:
            load_series = sample_load_power(time.index_range, time.periods)

        battery_cfg = base_simulation.battery_config_from_inputs(
            capacity_kwh,
            max_charge_kw,
            max_discharge_kw,
            charge_eff,
            discharge_eff,
            initial_soc,
        )

        simulation_setup = base_simulation.setup_from_inputs(
            time_cfg, solar_series, load_series, battery_cfg
        )
        simulation_results = base_simulation.run_simulation(simulation_setup)

        return (
            make_telemetry_figure(simulation_results.trajectory),
            make_metrics_table(simulation_results.metrics),
        )
