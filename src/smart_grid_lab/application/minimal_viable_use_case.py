"""
Use case: forecast-informed control of Microgrid with PV, Batterty and Load
for description see:
    rnd notes and materials/use_cases/PV-BATTERY-LOAD-GRID.md
"""

import pandas as pd

from smart_grid_lab.core import (
    Time,
    Solar,
    Load,
    Battery,
    Grid,
    SetUp,
    Simulation,
    Results,
)

from smart_grid_lab.core.controllers import Reactive

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
    controller: Reactive | None = None,
    use_bar=False,
) -> Results:

    time = time if time is not None else default_time()
    index = time.index_range

    solar_kw = solar_kw if solar_kw is not None else sample_solar_kW(time)
    solar_kw = solar_kw.reindex(index).astype(float)

    load_kw = load_kw if load_kw is not None else sample_load_kW(time)
    load_kw = load_kw.reindex(index).astype(float)

    # net_kw = solar_kw - load_kw # TODO need by forecaster needed by strateegy

    irradiance = solar_kw / Solar._PV_PLANT_AREA_M2

    battery = battery if battery is not None else default_battery()

    grid = grid if grid is not None else Grid()

    components = {
        "solar": Solar(irradiance),
        "load": Load(load_kw),
        "battery": battery,
        "grid": grid,
    }

    setup = SetUp(time=time, components=components)

    controller = Reactive()

    simulation = Simulation(setup, strategy=controller)

    trajectory = simulation.run(use_bar=use_bar)
    metrics = calculate_metrics(trajectory, time.step)

    return Results(trajectory=trajectory, metrics=metrics)


def calculate_metrics(
    trajectory: pd.DataFrame,
    step: pd.Timedelta,
) -> pd.DataFrame:
    # TODO re-implement
    """Summarize use case as UI-ready scalar KPIs."""
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

    return run_simulation(time, solar_kw, load_kw, battery)
