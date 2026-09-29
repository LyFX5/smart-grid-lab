"""
Use case: Control of Microgrid with PV, Load and Batterty
for experiment description see:
    rnd notes and materials/use_cases/PV-LOAD-BATTERY.md
"""

import pandas as pd

from smart_grid_lab.core import (
    Time,
    PV,
    Load,
    Battery,
    SetUp,
    Simulation,
    Results,
)

from smart_grid_lab.core.controllers import Reactive

from smart_grid_lab.domain.microgrid_configuration import PV_AREA_M2

from ..load_template import (
    default_time,
    default_battery,
    _synthetic_irradiance,
    _synthetic_load_kW,
)


def run_simulation(
    time: Time | None = None,
    pv_kw: pd.Series | None = None,
    load_kw: pd.Series | None = None,
    battery: Battery | None = None,
    controller: Reactive | None = None,
    use_bar=False,
) -> Results:

    time = time if time is not None else default_time()
    index = time.index_range

    pv_kw = (
        pv_kw
        if pv_kw is not None
        else _synthetic_irradiance(time) * PV_AREA_M2 / 1000.0
    )
    pv_kw = pv_kw.reindex(index).astype(float)

    load_kw = load_kw if load_kw is not None else _synthetic_load_kW(time)
    load_kw = load_kw.reindex(index).astype(float)

    battery = battery if battery is not None else default_battery()

    components = {
        "pv": PV(pv_kw),
        "load": Load(load_kw),
        "battery": battery,
    }

    setup = SetUp(time=time, components=components)

    controller = controller if controller is not None else Reactive()

    simulation = Simulation(setup, controller)

    trajectory = simulation.run(use_bar=use_bar)
    metrics = calculate_metrics(trajectory)

    return Results(trajectory=trajectory, metrics=metrics)


def calculate_metrics(
    trajectory: pd.DataFrame,
) -> pd.DataFrame:

    step = trajectory.index[1] - trajectory.index[0]

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
        "pv_energy_kwh": _energy_kwh("pv_power"),
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


from ..unpack_ui_input import (
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
    pv_kw: pd.Series,
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

    return run_simulation(time, pv_kw, load_kw, battery)
