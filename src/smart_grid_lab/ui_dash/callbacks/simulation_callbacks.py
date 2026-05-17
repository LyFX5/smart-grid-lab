from __future__ import annotations

import numpy as np
import pandas as pd
from dash import Input, Output, State

from smart_grid_lab.application.use_cases import demo_simulation
from smart_grid_lab.application.use_cases.off_grid_h2_forecast_control import (
    OffGridH2ForecastConfig,
    run_forecast_h2_offgrid_from_ui_battery,
)

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


def _solar_kw_from_irradiance(irradiance: pd.Series) -> pd.Series:
    # Mirrors the current Solar component default area (100 m²) so the same
    # synthetic sample can drive both the baseline UI and the H₂ use case.
    return irradiance.astype(float) * 100.0


def _positive_int(value, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(1, parsed)


def _float_or_default(value, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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
        time_cfg = demo_simulation.time_config_from_inputs(start, end, step_minutes)
        time = demo_simulation.build_time(time_cfg)
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
        time_cfg = demo_simulation.time_config_from_inputs(start, end, step_minutes)
        time = demo_simulation.build_time(time_cfg)
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
        State("control-use-case", "value"),
        State("forecast-model", "value"),
        State("forecast-horizon", "value"),
        State("forecast-window", "value"),
        State("h2-tank-capacity-kg", "value"),
        State("h2-tank-initial-level", "value"),
        State("electrolyser-current-max-a", "value"),
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
        control_use_case,
        forecast_model,
        forecast_horizon,
        forecast_window,
        tank_capacity_kg,
        tank_initial_level,
        electrolyser_current_max_a,
    ):
        if not n_clicks:
            return (
                results_elements.make_telemetry_figure(None),
                results_elements.make_metrics_table(None),
            )

        time_cfg = demo_simulation.time_config_from_inputs(start, end, step_minutes)
        time = demo_simulation.build_time(time_cfg)

        solar_series = _series_from_store(solar_data)
        if solar_series is None:
            solar_series = sample_solar_irradiance(time.index_range)

        load_series = _series_from_store(load_data)
        if load_series is None:
            load_series = sample_load_power(time.index_range, time.periods)

        if control_use_case == "forecast_h2":
            scenario = OffGridH2ForecastConfig(
                forecast_horizon=_positive_int(forecast_horizon, 6),
                forecast_window=_positive_int(forecast_window, 6),
                use_oracle_forecast=forecast_model != "rolling",
                tank_capacity_kg=max(1.0, _float_or_default(tank_capacity_kg, 50.0)),
                tank_initial_level=min(
                    0.95, max(0.0, _float_or_default(tank_initial_level, 0.2))
                ),
                electrolyser_current_max_a=max(
                    0.0, _float_or_default(electrolyser_current_max_a, 4.0)
                ),
            )
            simulation_results = run_forecast_h2_offgrid_from_ui_battery(
                time,
                _solar_kw_from_irradiance(solar_series),
                load_series,
                capacity_kwh,
                max_charge_kw,
                max_discharge_kw,
                charge_eff,
                discharge_eff,
                initial_soc,
                scenario,
            )
        else:
            battery_cfg = demo_simulation.battery_config_from_inputs(
                capacity_kwh,
                max_charge_kw,
                max_discharge_kw,
                charge_eff,
                discharge_eff,
                initial_soc,
            )

            simulation_setup = demo_simulation.setup_from_inputs(
                time_cfg, solar_series, load_series, battery_cfg
            )
            simulation_results = demo_simulation.run_simulation(simulation_setup)

        return (
            results_elements.make_telemetry_figure(simulation_results.trajectory),
            results_elements.make_metrics_table(simulation_results.metrics),
        )
