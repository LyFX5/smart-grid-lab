from dash import dcc, html
import plotly.graph_objects as go


def _placeholder_figure():
    fig = go.Figure()
    fig.update_layout(
        title="Microgrid Dynamics",
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


layout = html.Div(
    className="window1-layout",
    style={
        "display": "flex",
        "flexDirection": "row",
        "gap": "1rem",
        "minHeight": "100vh",
        "alignItems": "stretch",
    },
    children=[
        html.Div(
            className="setup-column",
            style={
                "width": "340px",
                "minWidth": "280px",
                "padding": "1rem 1.25rem",
                "borderRight": "1px solid #ddd",
                "overflowY": "auto",
                "display": "flex",
                "flexDirection": "column",
                "gap": "1rem",
            },
            children=[
                html.H2("Set Up Microgrid", style={"marginTop": 0}),
                html.Div(
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
                ),
                html.Div(
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
                ),
                html.Div(
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
                ),
                html.Div(
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
                        html.Label(
                            "Max discharge (kW)", htmlFor="battery-max-discharge-kw"
                        ),
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
                ),
                html.Button(
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
                ),
                dcc.Store(id="solar-profile-store", data=None),
                dcc.Store(id="load-profile-store", data=None),
            ],
        ),
        html.Div(
            className="figure-column",
            style={"flex": "1", "minWidth": 0, "padding": "1rem"},
            children=[
                dcc.Graph(
                    id="main-graph",
                    figure=_placeholder_figure(),
                    config={"displayModeBar": True},
                    style={"height": "85vh"},
                ),
            ],
        ),
    ],
)
