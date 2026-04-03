from typing import Dict
import pandas as pd
from .component import Component


class Solar(Component):

    def __init__(self, irradiance_profile: pd.Series):
        self.profile = irradiance_profile
        self.timestamp = self.profile.index[0]
        self.pv_plant_area = 100  # TODO configure not hardcode

    def irradiance(self) -> float:
        return self.profile[self.timestamp]

    def power(self) -> float:
        return self.pv_plant_area * self.irradiance()

    def state(self) -> Dict[str, float]:
        return {"timestamp": self.timestamp, "power": self.power()}

    def step(self, step_timedelta: pd.Timedelta):
        self.timestamp += step_timedelta
