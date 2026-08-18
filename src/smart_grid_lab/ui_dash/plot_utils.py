import plotly.graph_objects as go

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

primary_cols = [
    "solar_power",
    "load_power",
    "battery_available_power",
    "battery_charge_power",
    "battery_discharge_power",
    "electrolyser_power_kw",
]

secondary_cols = [
    "battery_soc",
    "hydrogen_tank_level",
]


def build_figure(df, primary_cols, secondary_cols):

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

    fig.update_yaxes(title_text="Power (kW)", secondary_y=False)
    fig.update_yaxes(
        title_text="State of charge / tank level (0–1)", secondary_y=True
    )

    return fig


# template="plotly_dark",
# paper_bgcolor="#0f172a",  # deep night blue
# plot_bgcolor="#0f172a",
# font=dict(color="#e5e7eb"),
# margin=dict(l=20, r=20, t=40, b=20),
legend = (
    dict(
        bgcolor="rgba(0,0,0,0)",
        # orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
)


def update_layout(fig, title):
    fig.update_layout(
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
    )
    fig.update_layout(title=title)
    return fig


def empty_figure():
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
    return fig


"""
df = sample_df.melt(
    id_vars="utc_timestamp",
    value_vars=["load", "pv", "grid", "battery"],
    var_name="category",
    value_name="power"
)


fig = px.line(
    df,
    x="utc_timestamp",
    y="power",
    color="category",
    title="3-Day Microgrid Energy Snapshot"
)

fig.update_layout(
    xaxis_title="Time",
    yaxis_title="Power",
    template="plotly_white",
    height=600
)

fig.show()
"""
