from typing import Tuple, Dict, Any
from dataclasses import dataclass
import pandas as pd

try:
    from tqdm import tqdm
except (
    ModuleNotFoundError
):  # pragma: no cover - exercised only in minimal envs

    def tqdm(iterable, disable=False):
        return iterable


from .time import Time
from .components import Component
from .microgrid import Microgrid
from .forecasting import PVForecastModel, LoadForecastModel
from .controllers import Controller, ForecastsInformed


@dataclass
class SetUp:
    time: Time
    components: Dict[str, Component]
    perfect_forecasts: bool
    pv_model: PVForecastModel
    load_model: LoadForecastModel
    tarif_model: pd.DataFrame


@dataclass
class Results:
    trajectory: pd.DataFrame
    metrics: pd.DataFrame


class Simulation:

    def __init__(self, setup: SetUp, controller=None):

        self.setup = setup

        self.steps = (
            self.setup.time.end - self.setup.time.start
        ) // self.setup.time.step

        self.microgrid = Microgrid(
            self.setup.time,
            self.setup.components,
            self.setup.perfect_forecasts,
            self.setup.pv_model,
            self.setup.load_model,
            self.setup.tarif_model,
        )
        self.controller = (
            controller if controller is not None else Controller()
        )

    def step(self) -> Tuple[Dict[str, Any], Dict[str, float]]:
        mcg_state = self.microgrid.state()
        if isinstance(self.controller, ForecastsInformed):
            forecasts = self.microgrid.forecasts()
            self.controller.step(mcg_state, forecasts)
        else:
            self.controller.step(mcg_state)
        action = self.controller.action()
        self.microgrid.step(action)
        return (mcg_state, action)

    def run(self, use_bar) -> pd.DataFrame:
        trajectory = []
        for _ in tqdm(range(self.steps), disable=not use_bar):
            mcg_state, action = self.step()
            trajectory.append(mcg_state)  # NOTE also can add action

        trajectory = pd.DataFrame(trajectory)
        trajectory = trajectory.set_index("timestamp")

        return trajectory
