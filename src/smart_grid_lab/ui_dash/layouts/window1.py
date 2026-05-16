from dash import dcc, html
from . import setup_elements
from . import results_elements


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
        setup_elements.time,
        setup_elements.control_use_case,
        setup_elements.solar_irradiance,
        setup_elements.load_power,
        setup_elements.battery,
        setup_elements.forecast_h2,
        setup_elements.run_button,
        dcc.Store(id="solar-profile-store", data=None),
        dcc.Store(id="load-profile-store", data=None),
    ],
)

results_column = html.Div(
    className="results-column",
    style={
        # "width": "340px",
        # "minWidth": "100%",
        "width": "100%",
        "padding": "1rem 1.25rem",
        "borderRight": "1px solid #ddd",
        "overflowY": "auto",
        "display": "flex",
        "flexDirection": "column",
        "gap": "1rem",
    },
    children=[results_elements.telemetry_figure, results_elements.metrics_table],
)


layout = html.Div(
    className="window1-layout",
    style={
        "display": "flex",
        "flexDirection": "row",
        "gap": "1rem",
        # "minHeight": "100vh",
        "alignItems": "stretch",
        # "backgroundColor": "#020617",
        "padding": "16px",
        "borderRadius": "12px",
        "boxShadow": "0 10px 30px rgba(0,0,0,0.3)",
    },
    children=[
        setup_column,
        results_column,
    ],
)
