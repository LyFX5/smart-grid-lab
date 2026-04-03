from typing import Dict
import pandas as pd
from .component import Component


class Load(Component):

    def __init__(self, power_profile: pd.Series):
        self.profile = power_profile
        self.timestamp = self.profile.index[0]

    def power(self) -> float:
        return self.profile[self.timestamp]

    def state(self) -> Dict[str, float]:
        return {"power": self.power()}

    def step(self, step_timedelta: pd.Timedelta):
        self.timestamp += step_timedelta
