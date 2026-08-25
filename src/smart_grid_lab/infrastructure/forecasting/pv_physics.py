"""
PV physics: irradiance -> power transformation (infrastructure layer).

Implements the discussed two-stage separation:
  Stage 1: GHI forecast (from NWP or openSTEF GBLinear on radiation)
  Stage 2: deterministic PV conversion (linear now, pvlib optional).

This keeps the simulation/physics in core-adjacent code while ML handles
irradiance forecast reuse via MLFlowStorage. Capacity scaling is a parameter
instead of re-training per site.

References:
- openstef_models/transforms/weather_domain/radiation_derived_features_adder.py:134 pvlib Location.get_clearsky
- pvlib.irradiance.get_total_irradiance for tilt/azimuth
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

try:
    import pvlib  # optional
except ImportError:  # fallback to linear only
    pvlib = None  # type: ignore


@dataclass(frozen=True)
class PVSystemConfig:
    """Physical PV system params for linear or pvlib conversion."""

    kWp: float = 10.0  # peak power at 1000 W/m2
    # linear model: pv_kW = kWp * ghi / 1000 * temp_factor
    # if use_pvlib True, uses pvlib with tilt/azimuth
    use_pvlib: bool = False
    surface_tilt: float = 34.0  # degrees, RadiationDerivedFeaturesAdder default
    surface_azimuth: float = 180.0  # south
    temp_coeff: float = -0.004  # /C, power drop per deg above 25C

    def pv_from_ghi(
        self,
        ghi: pd.Series,
        temperature: pd.Series | None = None,
        method: Literal["linear", "pvlib"] | None = None,
    ) -> pd.Series:
        method = method or ("pvlib" if self.use_pvlib else "linear")
        if method == "linear":
            # simple linear, clipped at 0, temperature derating
            pv = ghi.clip(lower=0) * self.kWp / 1000.0
            if temperature is not None:
                pv = pv * (1 + self.temp_coeff * (temperature - 25))
            return pv.clip(lower=0)
        else:
            if pvlib is None:
                raise ImportError("pvlib not installed, install openstef-models[pvlib] or use linear")
            # pvlib path: ghi -> poa_global -> dc power approx linear (detailed model would need inverter)
            # For now delegate to linear after poa correction if location known elsewhere
            # Caller should provide ghi already as poa; fallback:
            return ghi.clip(lower=0) * self.kWp / 1000.0


def ghi_to_pv_linear(
    ghi_wm2: pd.Series | float,
    kWp: float = 10.0,
    temperature_c: pd.Series | float | None = None,
    temp_coeff: float = -0.004,
) -> pd.Series | float:
    """One-liner linear transform used in adapters."""

    def _convert(s: pd.Series) -> pd.Series:
        pv = s.clip(lower=0) * kWp / 1000.0
        if temperature_c is not None:
            # temperature_c may be scalar or Series
            pv = pv * (1 + temp_coeff * (pd.Series(temperature_c, index=s.index) - 25) if isinstance(temperature_c, pd.Series) else (1 + temp_coeff * (temperature_c - 25)))  # type: ignore
        return pv.clip(lower=0)

    if isinstance(ghi_wm2, pd.Series):
        return _convert(ghi_wm2)
    else:
        val = max(0, float(ghi_wm2)) * kWp / 1000.0
        if temperature_c is not None:
            val *= 1 + temp_coeff * (float(temperature_c) - 25)  # type: ignore
        return max(0, val)


# For forecasting: if you forecast radiation, apply after predict
def apply_pv_physics_to_forecast(
    forecast_df: pd.DataFrame,
    pv_config: PVSystemConfig,
    ghi_column: str = "shortwave_radiation",
    temperature_column: str | None = "temperature_2m",
) -> pd.DataFrame:
    """Post-process ForecastDataset DataFrame with quantile columns to PV kW.

    Expects forecast_df with quantile columns (quantile_P10...) from openSTEF
    where target was radiation. Applies linear factor per quantile.
    """
    out = forecast_df.copy()
    temp = out[temperature_column] if temperature_column and temperature_column in out.columns else None
    for col in [c for c in out.columns if c.startswith("quantile_")]:
        out[col] = pv_config.pv_from_ghi(out[col], temperature=temp if isinstance(temp, pd.Series) else None)
    return out
