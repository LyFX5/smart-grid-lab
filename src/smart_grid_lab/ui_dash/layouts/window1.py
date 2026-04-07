from dash import dcc, html
from . import elements


setup_column = html.Div(
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
        elements.time,
        elements.solar_irradiance,
        elements.load_power,
        elements.battery,
        elements.run_button,
        dcc.Store(id="solar-profile-store", data=None),
        dcc.Store(id="load-profile-store", data=None),
    ],
)

results_column = html.Div(
    className="results-column",
    style={
        # "width": "340px",
        "minWidth": 0,
        "padding": "1rem 1.25rem",
        "borderRight": "1px solid #ddd",
        "overflowY": "auto",
        "display": "flex",
        "flexDirection": "column",
        "gap": "1rem",
    },
    children=[elements.telemetry_figure, elements.metrics_table],
)


layout = html.Div(
    className="window1-layout",
    style={
        "display": "flex",
        "flexDirection": "row",
        "gap": "1rem",
        # "minHeight": "100vh",
        "alignItems": "stretch",
    },
    children=[
        setup_column,
        results_column,
    ],
)
