from dash import dcc, html
from smart_grid_lab.domain.microgrid_configuration import (
    TimeConfig,
    BatteryConfig,
)

default_time_config = TimeConfig()


time = html.Div(
    [
        html.H4(
            "Time horizon",
            style={"margin": "0 0 0.5rem 0", "fontSize": "1rem"},
        ),
        html.Label("Start", htmlFor="time-start"),
        dcc.Input(
            id="time-start",
            type="text",
            value=default_time_config.start,
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label("End", htmlFor="time-end"),
        dcc.Input(
            id="time-end",
            type="text",
            value=default_time_config.end,
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label("Step (minutes)", htmlFor="time-step-minutes"),
        dcc.Input(
            id="time-step-minutes",
            type="number",
            value=default_time_config.step_minutes,
            min=1,
            step=1,
            style={"width": "100%"},
        ),
    ]
)

pv_power = html.Div(
    [
        html.H4(
            "PV power",
            style={"margin": "0 0 0.5rem 0", "fontSize": "1rem"},
        ),
        html.Button(
            "Use sample",
            id="btn-pv-sample",
            n_clicks=0,
            type="button",
            style={"width": "100%"},
        ),
    ]
)

load_power = html.Div(
    [
        html.H4(
            "Load power",
            style={"margin": "0 0 0.5rem 0", "fontSize": "1rem"},
        ),
        html.Button(
            "Use sample",
            id="btn-load-sample",
            n_clicks=0,
            type="button",
            style={"width": "100%"},
        ),
    ]
)


default_battery_config = BatteryConfig()


battery = html.Div(
    [
        html.H4(
            "Battery initialization",
            style={"margin": "0 0 0.5rem 0", "fontSize": "1rem"},
        ),
        html.Label("Capacity (kWh)", htmlFor="battery-capacity-kwh"),
        dcc.Input(
            id="battery-capacity-kwh",
            type="number",
            value=default_battery_config.capacity_kwh,
            min=0,
            step=0.1,
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label("Max charge (kW)", htmlFor="battery-max-charge-kw"),
        dcc.Input(
            id="battery-max-charge-kw",
            type="number",
            value=default_battery_config.max_charge_kw,
            min=0,
            step=0.1,
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label("Max discharge (kW)", htmlFor="battery-max-discharge-kw"),
        dcc.Input(
            id="battery-max-discharge-kw",
            type="number",
            value=default_battery_config.max_discharge_kw,
            min=0,
            step=0.1,
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label(
            "Max charge efficiency",
            htmlFor="battery-charge-efficiency",
        ),
        dcc.Input(
            id="battery-charge-efficiency",
            type="number",
            value=default_battery_config.max_charge_efficiency,
            min=0,
            max=1,
            step=0.01,
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label(
            "Max discharge efficiency",
            htmlFor="battery-discharge-efficiency",
        ),
        dcc.Input(
            id="battery-discharge-efficiency",
            type="number",
            value=default_battery_config.max_discharge_efficiency,
            min=0,
            max=1,
            step=0.01,
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label("Initial SOC (0–1)", htmlFor="battery-initial-soc"),
        dcc.Input(
            id="battery-initial-soc",
            type="number",
            value=default_battery_config.initial_soc,
            min=0,
            max=1,
            step=0.01,
            style={"width": "100%"},
        ),
    ]
)


run_button = html.Button(
    "Run Simulation",
    id="btn-run-simulation",
    n_clicks=0,
    type="button",
    style={
        "width": "100%",
        "padding": "0.6rem",
        "fontWeight": "600",
        "marginTop": "auto",
    },
)
