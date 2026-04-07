from dataclasses import dataclass
from pandas import Timestamp, Timedelta, date_range


@dataclass
class Time:

    start: Timestamp
    end: Timestamp
    step: Timedelta

    @property
    def periods(self):
        return int((self.end - self.start) // self.step)

    @property
    def index_range(self):
        return date_range(self.start, periods=self.periods, freq=self.step)
