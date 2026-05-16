from dash import dcc, html


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
            value="2026-03-15 12:00:00",
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label("End", htmlFor="time-end"),
        dcc.Input(
            id="time-end",
            type="text",
            value="2026-03-20 12:00:00",
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label("Step (minutes)", htmlFor="time-step-minutes"),
        dcc.Input(
            id="time-step-minutes",
            type="number",
            value=10,
            min=1,
            step=1,
            style={"width": "100%"},
        ),
    ]
)

solar_irradiance = html.Div(
    [
        html.H4(
            "Solar irradiance",
            style={"margin": "0 0 0.5rem 0", "fontSize": "1rem"},
        ),
        html.Button(
            "Use sample",
            id="btn-solar-sample",
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
            value=100,
            min=0,
            step=0.1,
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label("Max charge (kW)", htmlFor="battery-max-charge-kw"),
        dcc.Input(
            id="battery-max-charge-kw",
            type="number",
            value=30,
            min=0,
            step=0.1,
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label("Max discharge (kW)", htmlFor="battery-max-discharge-kw"),
        dcc.Input(
            id="battery-max-discharge-kw",
            type="number",
            value=30,
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
            value=0.95,
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
            value=0.95,
            min=0,
            max=1,
            step=0.01,
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label("Initial SOC (0–1)", htmlFor="battery-initial-soc"),
        dcc.Input(
            id="battery-initial-soc",
            type="number",
            value=0.5,
            min=0,
            max=1,
            step=0.01,
            style={"width": "100%"},
        ),
    ]
)


control_use_case = html.Div(
    [
        html.H4(
            "Control use case",
            style={"margin": "0 0 0.5rem 0", "fontSize": "1rem"},
        ),
        dcc.RadioItems(
            id="control-use-case",
            options=[
                {"label": "Battery baseline", "value": "battery_baseline"},
                {"label": "Forecast H₂ control", "value": "forecast_h2"},
            ],
            value="battery_baseline",
            labelStyle={"display": "block", "marginBottom": "0.35rem"},
        ),
        html.P(
            "Forecast H₂ mode converts the synthetic solar sample to kW "
            "and runs the off-grid electrolyser + tank use case.",
            style={"fontSize": "12px", "margin": "0.5rem 0 0", "color": "#64748b"},
        ),
    ]
)

forecast_h2 = html.Div(
    [
        html.H4(
            "Forecast H₂ controls",
            style={"margin": "0 0 0.5rem 0", "fontSize": "1rem"},
        ),
        html.Label("Forecast model", htmlFor="forecast-model"),
        dcc.Dropdown(
            id="forecast-model",
            options=[
                {
                    "label": "Oracle mean surplus (synthetic benchmark)",
                    "value": "oracle",
                },
                {
                    "label": "Rolling mean surplus (causal baseline)",
                    "value": "rolling",
                },
            ],
            value="oracle",
            clearable=False,
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label("Forecast horizon (steps)", htmlFor="forecast-horizon"),
        dcc.Input(
            id="forecast-horizon",
            type="number",
            value=6,
            min=1,
            step=1,
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label("Rolling window (steps)", htmlFor="forecast-window"),
        dcc.Input(
            id="forecast-window",
            type="number",
            value=6,
            min=1,
            step=1,
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label("Tank capacity (kg)", htmlFor="h2-tank-capacity-kg"),
        dcc.Input(
            id="h2-tank-capacity-kg",
            type="number",
            value=50,
            min=1,
            step=1,
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label("Initial tank level (0–1)", htmlFor="h2-tank-initial-level"),
        dcc.Input(
            id="h2-tank-initial-level",
            type="number",
            value=0.2,
            min=0,
            max=0.95,
            step=0.01,
            style={"width": "100%", "marginBottom": "0.5rem"},
        ),
        html.Label("Electrolyser max current (A)", htmlFor="electrolyser-current-max-a"),
        dcc.Input(
            id="electrolyser-current-max-a",
            type="number",
            value=4,
            min=0,
            step=0.1,
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
