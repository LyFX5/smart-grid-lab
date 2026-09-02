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
from .controllers import Controller


@dataclass
class SetUp:
    time: Time
    components: Dict[str, Component]


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

        self.microgrid = Microgrid(self.setup.time, self.setup.components)
        self.controller = (
            controller if controller is not None else Controller()
        )

    def step(self) -> Tuple[Dict[str, Any], Dict[str, float]]:
        mcg_state = self.microgrid.state()
        self.strategy.step(mcg_state)
        action = self.strategy.action()
        self.microgrid.step(action)
        return (mcg_state, action)

    def run(self, use_bar) -> pd.DataFrame:
        trajectory = []
        for _ in tqdm(range(self.steps), disable=not use_bar):
            mcg_state, action = self.step()
            trajectory.append(mcg_state)  # NOTE also can add action
        trajectory = pd.DataFrame(trajectory)

        trajectory = trajectory.rename(
            columns={"solar_timestamp": "timestamp"}
        )  # TODO not here
        trajectory = trajectory.set_index("timestamp")

        return trajectory
