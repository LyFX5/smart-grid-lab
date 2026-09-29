from pandas import Series
from .power_profile import PowerProfile


class PV(PowerProfile):

    def __init__(self, power_profile: Series):
        super().__init__(power_profile)
