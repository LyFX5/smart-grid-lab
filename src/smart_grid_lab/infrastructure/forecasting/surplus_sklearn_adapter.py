"""
Sklearn (or similar) surplus forecast adapter — inference lives here.

Implements the core `SurplusForecastModel` contract. Wire a trained model
path when available; until then this falls back to persistence at `at`.

For ML-backed surplus (e.g. irradiance->pv physics), prefer
OpenSTEFGBLinearPVForecastAdapter + PVSystemConfig.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from smart_grid_lab.core.forecasting import SurplusForecastModel


class SklearnSurplusForecastAdapter(SurplusForecastModel):
    def __init__(
        self,
        model_path: Optional[str] = None,
        mlflow_storage=None,  # optional MLFlowStorage for sklearn model
        model_id: str = "surplus_sklearn",
    ) -> None:
        self._model_path = Path(model_path) if model_path else None
        self._mlflow_storage = mlflow_storage
        self._model_id = model_id
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return self._model
        if self._mlflow_storage is not None:
            runs = self._mlflow_storage.search_latest_runs(self._model_id)
            if runs:
                self._model = self._mlflow_storage.load_run_model(runs[0].info.run_id, self._model_id)
                return self._model
        if self._model_path and self._model_path.exists():
            import joblib

            self._model = joblib.load(self._model_path)
            return self._model
        return None

    def forecast_surplus_kw(self, net_kw: pd.Series, at: pd.Timestamp) -> float:
        model = self._load_model()
        if model is None:
            return float(net_kw.loc[at])
        # Generic sklearn: expect model.predict([[features]]) -> surplus
        # Caller should have engineered features; fallback to direct
        try:
            # try simple 1-step: use last value as feature
            import numpy as np

            feat = np.array([[float(net_kw.loc[at])]])
            return float(model.predict(feat)[0])
        except Exception as e:
            raise NotImplementedError(f"SklearnSurplusForecastAdapter: wire predict mapping for {self._model_path!r}: {e}") from e
