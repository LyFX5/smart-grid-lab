from dash import dcc, html
import plotly.graph_objects as go

import pandas as pd


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


def _placeholder_telemetry_figure():
    fig = go.Figure()
    fig.update_layout(
        title="Microgrid Telemetry",
        annotations=[
            dict(
                text='Click "Run Simulation" to compute results.',
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


telemetry_figure = html.Div(
    className="telemetry-figure",
    style={"flex": "1", "minWidth": 0, "padding": "1rem"},
    children=[
        dcc.Graph(
            id="telemetry-figure",
            figure=_placeholder_telemetry_figure(),
            config={"displayModeBar": True},
            style={"height": "85vh"},
        ),
    ],
)

df = pd.DataFrame()

metrics_table = html.Div(
    className="metrics-table",
    style={"flex": "1", "minWidth": 0, "padding": "1rem"},
    children=[
        html.Table(
            [
                html.Thead(html.Tr([html.Th(col) for col in df.columns])),
                html.Tbody(
                    [
                        html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
                        for i in range(len(df))
                    ]
                ),
            ],
            id="metrics-table",
        )
    ],
)
