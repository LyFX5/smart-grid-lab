"""
Use case: forecast-informed control of Microgrid with PV, Load, Batterty, Electrolysers and H2-Tank
for description see:
    rnd notes and materials/use_cases/BATTERY-H2-FORECASTS.md
"""

import pandas as pd

from smart_grid_lab.core import (
    Time,
    Solar,
    Load,
    Battery,
    Electrolyser,
    HydrogenTank,
    Grid,
    SetUp,
    Simulation,
    Results,
)

from smart_grid_lab.core.controllers import ForecastsInformedRulesBased

from smart_grid_lab.domain.builders import H2Config

from .load_template import (
    default_time,
    default_battery,
    sample_solar_kW,
    sample_load_kW,
)


def run_simulation(
    time: Time | None = None,
    solar_kw: pd.Series | None = None,
    load_kw: pd.Series | None = None,
    battery: Battery | None = None,
    grid: Grid | None = None,
    h2_config: H2Config | None = None,
    controller: ForecastsInformedRulesBased | None = None,
    use_bar=False,
) -> Results:

    time = time if time is not None else default_time()
    index = time.index_range

    solar_kw = solar_kw if solar_kw is not None else sample_solar_kW(time)
    solar_kw = solar_kw.reindex(index).astype(float)

    load_kw = load_kw if load_kw is not None else sample_load_kW(time)
    load_kw = load_kw.reindex(index).astype(float)

    irradiance = solar_kw / Solar._PV_PLANT_AREA_M2

    battery = battery if battery is not None else default_battery()

    grid = grid if grid is not None else Grid()

    h2_config = h2_config if h2_config is not None else H2Config()
    num_of_elys = 4
    elys = [
        Electrolyser(
            i,
            h2_config.electrolyser_current_max_a,
            h2_config.temperature_ambient_c,
        )
        for i in range(num_of_elys)
    ]
    tank = HydrogenTank(
        h2_config.tank_capacity_kg, h2_config.tank_initial_level
    )

    components = {
        "solar": Solar(irradiance),
        "load": Load(load_kw),
        "battery": battery,
        "grid": grid,
        "electrolyser_1": elys[0],
        "electrolyser_2": elys[1],
        "electrolyser_3": elys[2],
        "electrolyser_4": elys[3],
        "hydrogen_tank": tank,
    }

    setup = SetUp(time=time, components=components)

    simulation = Simulation(setup, controller)

    trajectory = simulation.run(use_bar=use_bar)
    metrics = calculate_metrics(trajectory, time.step)

    return Results(trajectory=trajectory, metrics=metrics)


def calculate_metrics(
    trajectory: pd.DataFrame,
    step: pd.Timedelta,
) -> pd.DataFrame:
    # TODO re-implement
    """Summarize the forecast H₂ use case as UI-ready scalar KPIs."""
    step_h = step.total_seconds() / 3600.0

    def _energy_kwh(column: str, scale: float = 1.0) -> float | None:
        if column not in trajectory.columns:
            return None
        return round(float((trajectory[column] * scale).sum() * step_h), 3)

    final_row = (
        trajectory.iloc[-1] if not trajectory.empty else pd.Series(dtype=float)
    )
    metrics = {
        "solar_energy_kwh": _energy_kwh("solar_power"),
        "load_energy_kwh": _energy_kwh("load_power"),
        "electrolyser_energy_kwh": _energy_kwh(
            "electrolyser_power", scale=1 / 1000.0
        ),
        "hydrogen_produced_kg": None,
        "final_tank_level": None,
        "final_battery_soc": None,
        "electrolyser_degradation": None,
    }
    if "electrolyser_hydrogen_production" in trajectory.columns:
        metrics["hydrogen_produced_kg"] = round(
            float(
                trajectory["electrolyser_hydrogen_production"].sum() * step_h
            ),
            3,
        )
    if "hydrogen_tank_level" in trajectory.columns and not trajectory.empty:
        metrics["final_tank_level"] = round(
            float(final_row["hydrogen_tank_level"]), 3
        )
    if "battery_soc" in trajectory.columns and not trajectory.empty:
        metrics["final_battery_soc"] = round(
            float(final_row["battery_soc"]), 3
        )
    if (
        "electrolyser_degradation" in trajectory.columns
        and not trajectory.empty
    ):
        metrics["electrolyser_degradation"] = round(
            float(final_row["electrolyser_degradation"]), 3
        )

    return pd.DataFrame([metrics])


from .unpack_ui_input import (
    time_config_from_inputs,
    battery_config_from_inputs,
)
from smart_grid_lab.domain.builders import (
    build_time,
    build_battery,
)


def run_from_ui(
    start: str,
    end: str,
    step_minutes: int | float | None,
    solar_kw: pd.Series,
    load_kw: pd.Series,
    battery_capacity_kwh: float,
    battery_max_charge_kw: float,
    battery_max_discharge_kw: float,
    battery_charge_eff: float,
    battery_discharge_eff: float,
    battery_initial_soc: float,
) -> Results:

    time_config = time_config_from_inputs(start, end, step_minutes)
    time = build_time(time_config)

    battery_config = battery_config_from_inputs(
        battery_capacity_kwh,
        battery_max_charge_kw,
        battery_max_discharge_kw,
        battery_charge_eff,
        battery_discharge_eff,
        battery_initial_soc,
    )
    battery = build_battery(battery_config)

    # TODO unpack h2_config and forecasters config

    return run_simulation(time, solar_kw, load_kw, battery)
