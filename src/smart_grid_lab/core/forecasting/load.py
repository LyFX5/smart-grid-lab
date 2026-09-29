from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class LoadForecastModel(ABC):

    @abstractmethod
    def forecast_load_kW(
        self, history: pd.Series, at: pd.Timestamp, horizon: pd.Timedelta
    ) -> pd.Series: ...
