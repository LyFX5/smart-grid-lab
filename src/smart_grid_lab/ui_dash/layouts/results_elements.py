import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from plotly.subplots import make_subplots

from ..plot_utils import (
    build_figure,
    update_layout,
    empty_figure,
    primary_cols,
    secondary_cols,
)


def make_telemetry_figure(telemetry_df: pd.DataFrame | None):
    if telemetry_df is not None:
        fig = build_figure(telemetry_df, primary_cols, secondary_cols)
    else:
        fig = empty_figure()
    fig = update_layout(fig, title="Microgrid Telemetry")
    return fig


telemetry_figure = html.Div(
    className="telemetry-figure",
    # style={"flex": "1", "minWidth": 0, "padding": "1rem"},
    children=dcc.Graph(
        id="telemetry-figure",
        figure=make_telemetry_figure(None),
        config={"displayModeBar": True},
        style={"height": "85vh"},
    ),
)


def make_metrics_table(metrics_table: pd.DataFrame | None):
    if metrics_table is None:
        metrics_table = pd.DataFrame()
    table = html.Table(
        children=[
            html.Thead(
                html.Tr([html.Th(col) for col in metrics_table.columns]),
                style={
                    # "backgroundColor": "#1e293b",
                    "fontWeight": "600",
                    # "padding": "16px",
                    "borderBottom": "1px solid #334155",
                    "textAlign": "left",
                },
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(metrics_table.iloc[i][col])
                            for col in metrics_table.columns
                        ]
                    )
                    for i in range(len(metrics_table))
                ],
            ),
        ],
        style={
            # "width": "100%",
            "borderCollapse": "collapse",
            # "backgroundColor": "#0f172a",
            # "color": "#e5e7eb",
            "fontSize": "14px",
            # "padding": "16px",
            "borderRadius": "6px",  # 6px ?
            "boxShadow": "0 10px 30px rgba(0,0,0,0.3)",
        },
    )
    return table


metrics_table = html.Div(
    id="metrics-table",
    className="metrics-table",
    # style={"flex": "1", "minWidth": 0, "padding": "1rem"},
    children=[
        html.H2("Metrics Table", style={"marginTop": 0, "fontSize": "14px"}),
        make_metrics_table(None),
    ],
)
