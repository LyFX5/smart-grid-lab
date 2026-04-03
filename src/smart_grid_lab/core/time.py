from dataclasses import dataclass
from pandas import Timestamp, Timedelta


@dataclass
class Time:

    start: Timestamp
    end: Timestamp
    step: Timedelta
