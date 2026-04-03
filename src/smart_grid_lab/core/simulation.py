from typing import Tuple, Dict
from dataclasses import dataclass
import pandas as pd
from tqdm import tqdm
from .time import Time
from .components import Component
from .microgrid import Microgrid
from .controllers import Strategy


@dataclass
class SetUp:
    time: Time
    components: Dict[str, Component]
    # TODO control


@dataclass
class Result:
    trajectory: pd.DataFrame
    # TODO implement metrics: pd.DataFrame


class Simulation:

    def __init__(self, setup: SetUp):

        self.setup = setup

        self.steps = (
            self.setup.time.end - self.setup.time.start
        ) // self.setup.time.step

        self._init_microgrid()
        self._init_strategy()

    def _init_microgrid(self):
        self.microgrid = Microgrid(self.setup.time, self.setup.components)

    def _init_strategy(self):
        self.strategy = Strategy()  # TODO init from SetUp

    def _step(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        mcg_state = self.microgrid.state()
        self.strategy.step(mcg_state)
        action = self.strategy.action()
        self.microgrid.step(action)
        return (mcg_state, action)

    def run(self, use_bar) -> Result:
        trajectory = []
        for _ in tqdm(range(self.steps), disable=not use_bar):
            (mcg_state, action) = self._step()
            trajectory.append(mcg_state)
        self.trajectory = pd.DataFrame(trajectory)

        self.trajectory = self.trajectory.rename(
            columns={"solar_timestamp": "timestamp"}
        )  # TODO not here
        self.trajectory = self.trajectory.set_index("timestamp")

        return Result(self.trajectory)

    def calculate_metrics(self):  # evaluate performance
        ...
