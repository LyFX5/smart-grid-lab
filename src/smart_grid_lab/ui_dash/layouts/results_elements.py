import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from plotly.subplots import make_subplots


colors = {
    "solar_power": "#f59e0b",  # amber sun
    "load_power": "#60a5fa",  # blue demand
    "battery_available_power": "blue",
    "battery_charge_power": "#34d399",  # green storing
    "battery_discharge_power": "#f87171",  # red releasing
    "electrolyser_power_kw": "#a855f7",  # purple flexible H₂ load
    "hydrogen_tank_level": "#14b8a6",  # teal storage level
}

cell_style = {
    "padding": "6px 8px",
    "borderBottom": "1px solid rgba(255,255,255,0.05)",
}


def make_telemetry_figure(telemetry_df: pd.DataFrame | None):
    if telemetry_df is not None:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        plot_df = telemetry_df.copy()
        if "electrolyser_power" in plot_df.columns:
            plot_df["electrolyser_power_kw"] = plot_df["electrolyser_power"] / 1000.0

        left_cols = [
            "solar_power",
            "load_power",
            "battery_available_power",
            "battery_charge_power",
            "battery_discharge_power",
            "electrolyser_power_kw",
        ]
        right_cols = ["battery_soc", "hydrogen_tank_level"]

        for col in left_cols:
            if col in plot_df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=plot_df.index,
                        y=plot_df[col],
                        name=col,
                        line={"color": colors.get(col)},
                    ),
                    secondary_y=False,
                )

        for col in right_cols:
            if col in plot_df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=plot_df.index,
                        y=plot_df[col],
                        name=col,
                        line={"color": colors.get(col)},
                    ),
                    secondary_y=True,
                )
        fig.update_yaxes(title_text="Power (kW)", secondary_y=False)
        fig.update_yaxes(title_text="State of charge / tank level (0–1)", secondary_y=True)
    else:
        fig = go.Figure()
        fig.update_layout(
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
            ]
        )
    fig.update_layout(
        # template="plotly_dark",
        # paper_bgcolor="#0f172a",  # deep night blue
        # plot_bgcolor="#0f172a",
        # font=dict(color="#e5e7eb"),
        # margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            # orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
    )
    fig.update_layout(title="Microgrid Dynamics")
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
