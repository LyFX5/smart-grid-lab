from __future__ import annotations

import pandas as pd
from dash import Input, Output, State

from smart_grid_lab.application.use_cases import pv_load_battery

from smart_grid_lab.application.load_template import (
    load_pv_kW,
    load_load_kW,
)

from smart_grid_lab.application.unpack_ui_input import (
    time_config_from_inputs,
    battery_config_from_inputs,
)

from smart_grid_lab.domain.builders import build_time, build_battery

from smart_grid_lab.ui_dash.layouts import results_elements


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


def register_simulation_callbacks(app) -> None:

    @app.callback(
        Output("pv-profile-store", "data"),
        Input("btn-pv-sample", "n_clicks"),
        State("time-start", "value"),
        State("time-end", "value"),
        State("time-step-minutes", "value"),
        prevent_initial_call=True,
    )
    def load_pv_sample(_n_clicks, start, end, step_minutes):
        time_config = time_config_from_inputs(start, end, step_minutes)
        time = build_time(time_config)
        pv_sample = load_pv_kW(time)
        pv_sample_as_dict = _series_to_store(pv_sample)
        return pv_sample_as_dict

    @app.callback(
        Output("load-profile-store", "data"),
        Input("btn-load-sample", "n_clicks"),
        State("time-start", "value"),
        State("time-end", "value"),
        State("time-step-minutes", "value"),
        prevent_initial_call=True,
    )
    def load_load_sample(_n_clicks, start, end, step_minutes):
        time_config = time_config_from_inputs(start, end, step_minutes)
        time = build_time(time_config)
        load_sample = load_load_kW(time)
        load_sample_as_dict = _series_to_store(load_sample)
        return load_sample_as_dict

    @app.callback(
        Output("trajectory-figure", "figure"),
        Output("metrics-table", "children"),
        Input("btn-run-simulation", "n_clicks"),
        State("pv-profile-store", "data"),
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
        pv_data,
        load_data,
        start,
        end,
        step_minutes,
        capacity_kwh,
        max_charge_kw,
        max_discharge_kw,
        max_charge_efficiency,
        max_discharge_efficiency,
        initial_soc,
    ):
        if not n_clicks:
            return (
                results_elements.make_trajectory_figure(None),
                results_elements.make_metrics_table(None),
            )

        time_config = time_config_from_inputs(start, end, step_minutes)
        time = build_time(time_config)

        pv_sample = _series_from_store(pv_data)
        if pv_sample is None:
            pv_sample = load_pv_kW(time)

        load_sample = _series_from_store(load_data)
        if load_sample is None:
            load_sample = load_load_kW(time)

        """
        NOTE latter it is possible to configure the choice of use case here
        if use_case == "grid_tariff":
            ...
        elif use_case == "h2":
            ...
        else:
        """

        battery_config = battery_config_from_inputs(
            capacity_kwh,
            max_charge_kw,
            max_discharge_kw,
            max_charge_efficiency,
            max_discharge_efficiency,
            initial_soc,
        )
        battery = build_battery(battery_config)

        results = pv_load_battery.run_simulation(
            time, pv_sample, load_sample, battery
        )

        return (
            results_elements.make_trajectory_figure(results.trajectory),
            results_elements.make_metrics_table(results.metrics),
        )
