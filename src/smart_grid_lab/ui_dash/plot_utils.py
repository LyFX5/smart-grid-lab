import plotly.graph_objects as go

from plotly.subplots import make_subplots

colors = {
    "pv_power": "#f59e0b",  # amber sun
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

primary_cols = [
    "pv_power",
    "load_power",
    "battery_available_power",
    "battery_charge_power",
    "battery_discharge_power",
    "grid_export_power",
    "grid_import_power",
    "grid_export_limit_violation",
    "grid_import_limit_violation",
    "remaining_power",
]

secondary_cols = [
    "battery_soc",
    "battery_soc_computational_error",
]


def build_figure(
    df,
    primary_cols,
    secondary_cols,
    title="Microgrid Trajectory",
    primary_y_title="Power (kW)",
    secondary_y_title="State of charge / tank level (0–1)",
):

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    df = df.copy()

    for col in primary_cols:
        if col in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    name=col,
                    line={"color": colors.get(col)},
                ),
                secondary_y=False,
            )

    for col in secondary_cols:
        if col in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    name=col,
                    line={"color": colors.get(col)},
                ),
                secondary_y=True,
            )

    fig.update_yaxes(title_text=primary_y_title, secondary_y=False)
    fig.update_yaxes(title_text=secondary_y_title, secondary_y=True)

    fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
    )
    fig.update_layout(title=title)

    return fig


def empty_figure(title="Microgrid Trajectory"):
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
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
    )
    fig.update_layout(title=title)
    return fig
