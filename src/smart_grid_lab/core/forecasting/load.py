from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class LoadForecastModel(ABC):

    @abstractmethod
    def forecast_load_kW(
        self,
        history: pd.Series,
        at: pd.Timestamp,
    ) -> float:
        """Return scalar forecast of load (kW) at decision time `at`."""
        # TODO or a Serias on horizon?
