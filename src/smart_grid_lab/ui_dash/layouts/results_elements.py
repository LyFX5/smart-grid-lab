import pandas as pd

from dash import dcc, html

from smart_grid_lab.ui_dash.plot_utils import (
    build_figure,
    empty_figure,
    primary_cols,
    secondary_cols,
)


def make_trajectory_figure(trajectory_df: pd.DataFrame | None):
    if trajectory_df is not None:
        fig = build_figure(trajectory_df, primary_cols, secondary_cols)
    else:
        fig = empty_figure()
    return fig


trajectory_figure = html.Div(
    className="trajectory-figure",
    style={"flex": "1", "minWidth": 0, "padding": "1rem"},
    children=dcc.Graph(
        id="trajectory-figure",
        figure=make_trajectory_figure(None),
        config={"displayModeBar": True},
        style={"height": "85vh"},
    ),
)


def make_metrics_table(metrics_table: pd.DataFrame | None):
    # Handle empty or missing data gracefully
    if metrics_table is None or metrics_table.empty:
        return html.Div(
            "No metrics available.",
            style={
                "color": "#94a3b8",
                "padding": "1rem",
                "textAlign": "center",
            },
        )

    # 1. Reset index so the metric names become a regular column named 'Metric'
    df = metrics_table.reset_index()
    if "index" in df.columns:
        df.rename(columns={"index": "Metric"}, inplace=True)

    columns = df.columns

    # 2. Define Styles (Matching your dark theme screenshot)
    header_style = {
        "backgroundColor": "transparent",
        "color": "#94a3b8",
        "fontWeight": "600",
        "padding": "12px 16px",
        "borderBottom": "1px solid #334155",
        "textAlign": "left",
        "fontSize": "12px",
        "textTransform": "uppercase",
        "letterSpacing": "0.05em",
    }

    # Specific style for the "Metric" header to align with the data
    metric_header_style = {**header_style, "textAlign": "left", "width": "60%"}
    value_header_style = {**header_style, "textAlign": "right"}

    row_style = {
        "borderBottom": "1px solid #1e293b",
    }

    metric_cell_style = {
        "padding": "12px 16px",
        "color": "#e2e8f0",
        "fontWeight": "600",
        "fontSize": "14px",
        "textAlign": "left",
    }

    value_cell_style = {
        "padding": "12px 16px",
        "color": "#e2e8f0",
        "fontFamily": "monospace",
        "fontSize": "14px",
        "textAlign": "right",
    }

    # 3. Build the Table
    table = html.Table(
        children=[
            html.Thead(
                html.Tr(
                    [
                        html.Th("Metric", style=metric_header_style),
                        *[
                            html.Th(col, style=value_header_style)
                            for col in columns
                            if col != "Metric"
                        ],
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            # First cell: Metric Name
                            html.Td(row["Metric"], style=metric_cell_style),
                            # Subsequent cells: Values
                            *[
                                html.Td(
                                    (
                                        f"{row[col]:,.2f}"
                                        if isinstance(row[col], float)
                                        else str(row[col])
                                    ),
                                    style=value_cell_style,
                                )
                                for col in columns
                                if col != "Metric"
                            ],
                        ],
                        style=row_style,
                    )
                    for _, row in df.iterrows()
                ]
            ),
        ],
        style={
            "width": "100%",
            "borderCollapse": "collapse",
            "backgroundColor": "#0f172a",  # Dark background from screenshot
            "color": "#e5e7eb",
            "fontSize": "14px",
            "borderRadius": "8px",
            "boxShadow": "0 4px 6px -1px rgba(0, 0, 0, 0.5)",
            "overflow": "hidden",  # Ensures border-radius clips the corners
        },
    )

    return table


metrics_table = html.Div(
    id="metrics-table",
    className="metrics-table",
    style={"flex": "1", "minWidth": 0, "padding": "1rem"},
    children=[
        html.H2(
            "Metrics",
            style={"marginTop": 0, "fontSize": "16px", "color": "#f8fafc"},
        ),
        make_metrics_table(None),
    ],
)
