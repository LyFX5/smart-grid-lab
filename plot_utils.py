import plotly.graph_objects as go

from plotly.subplots import make_subplots


class TelemertyPlotter:

    DEFAULT_COLORS = {
        "solar_power": "#f59e0b",
        "load_power": "#3b82f6",
        "battery_available_power": "#10b981",
        "battery_charge_power": "#06b6d4",
        "battery_discharge_power": "#ef4444",
        "electrolyser_power_kw": "#8b5cf6",
        "battery_soc": "#f97316",
        "hydrogen_tank_level": "#ec4899",
    }

    def __init__(
        self,
        telemetry_df,
        colors=None,
        title="Microgrid Dynamics",
        primary_cols=[
            "solar_power",
            "load_power",
            "battery_available_power",
            "battery_charge_power",
            "battery_discharge_power",
            "electrolyser_power_kw",
        ],
        secondary_cols=[
            "battery_soc",
            "hydrogen_tank_level",
        ],
    ):
        self.df = telemetry_df.copy()
        self.colors = colors or self.DEFAULT_COLORS
        self.title = title
        self.primary_cols = primary_cols
        self.secondary_cols = secondary_cols
        self._prepare_dataframe()

    def _prepare_dataframe(self):
        """
        if "electrolyser_power" in self.df.columns:
            self.df["electrolyser_power_kw"] = (
                self.df["electrolyser_power"] / 1000.0
            )
        """
        ...

    def build_figure(self):

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # -------------------------
        # left axis
        # -------------------------

        for col in self.primary_cols:

            if col not in self.df.columns:
                continue

            fig.add_trace(
                go.Scatter(
                    x=self.df.index,
                    y=self.df[col],
                    name=col,
                    line={"color": self.colors.get(col)},
                ),
                secondary_y=False,
            )

        # -------------------------
        # right axis
        # -------------------------

        for col in self.secondary_cols:

            if col not in self.df.columns:
                continue

            fig.add_trace(
                go.Scatter(
                    x=self.df.index,
                    y=self.df[col],
                    name=col,
                    line={"color": self.colors.get(col)},
                ),
                secondary_y=True,
            )

        # -------------------------
        # axes
        # -------------------------

        fig.update_yaxes(
            title_text="Power (kW)",
            secondary_y=False,
        )

        fig.update_yaxes(
            title_text="SOC / Tank Level",
            secondary_y=True,
            range=[0, 1],
        )

        # -------------------------
        # layout
        # -------------------------

        fig.update_layout(
            title=self.title,
            legend=dict(
                bgcolor="rgba(0,0,0,0)",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(255,255,255,0.05)",
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(255,255,255,0.05)",
            ),
            height=650,
        )

        return fig

    def show(self):
        fig = self.build_figure()
        # fig.show()
        return fig


"""
plot_df = sample_df.melt(
    id_vars="utc_timestamp",
    value_vars=["load", "pv", "grid", "battery"],
    var_name="category",
    value_name="power"
)


fig = px.line(
    plot_df,
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
