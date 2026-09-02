from typing import Dict
import pandas as pd
from .component import Component


class Solar(Component):

    _PV_PLANT_AREA_M2 = 100.0  # TODO configure not hardcode

    def __init__(self, irradiance_profile: pd.Series):
        self.profile = irradiance_profile
        self.timestamp = self.profile.index[0]
        self.pv_plant_area = Solar._PV_PLANT_AREA_M2

    def irradiance(self) -> float:
        return self.profile[self.timestamp]

    def power(self) -> float:
        return self.pv_plant_area * self.irradiance()

    def state(self) -> Dict[str, float]:
        return {"timestamp": self.timestamp, "power": self.power()}

    def step(self, step_timedelta: pd.Timedelta):
        self.timestamp += step_timedelta
