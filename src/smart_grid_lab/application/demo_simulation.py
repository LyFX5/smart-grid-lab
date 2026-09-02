import pandas as pd

from smart_grid_lab.core import (
    Solar,
    Load,
    SetUp,
    Results,
    Simulation,
)

from smart_grid_lab.domain.builders import (
    TimeConfig,
    build_time,
    BatteryConfig,
    build_battery,
)


def setup_from_inputs(
    time_cfg: TimeConfig,
    solar_series: pd.Series,
    load_series: pd.Series,
    battery_cfg: BatteryConfig,
) -> SetUp:
    time = build_time(time_cfg)
    components = {
        "solar": Solar(solar_series),
        "load": Load(load_series),
        "battery": build_battery(battery_cfg),
    }
    return SetUp(time, components)


def run_simulation(setup: SetUp) -> Results:
    simulation = Simulation(setup)
    trajectory = simulation.run(use_bar=False)
    metrics = simulation.calculate_metrics(trajectory)
    return Results(trajectory, metrics)
