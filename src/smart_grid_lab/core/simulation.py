from typing import Tuple, Dict, Any
from dataclasses import dataclass
import pandas as pd
from tqdm import tqdm

"""
try:
    from tqdm import tqdm
except (
    ModuleNotFoundError
):  # pragma: no cover - exercised only in minimal envs

    def tqdm(iterable, disable=False):
        return iterable
"""


from .microgrid import Microgrid
from .controllers import Controller, ForecastsInformed


@dataclass
class Results:
    trajectory: pd.DataFrame
    metrics: pd.DataFrame


class Simulation:

    def __init__(self, microgrid: Microgrid, controller: Controller):
        self.steps = (
            microgrid.time.end - microgrid.time.start
        ) // microgrid.time.step - 1 * 24 * 4  # TODO do not hardcode
        self.microgrid = microgrid
        self.controller = controller

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
            trajectory.append(mcg_state)
            # NOTE also can add action
            # and also can add forecasts (or forecasts[0])

        trajectory = pd.DataFrame(trajectory)
        trajectory = trajectory.set_index("timestamp")

        return trajectory
