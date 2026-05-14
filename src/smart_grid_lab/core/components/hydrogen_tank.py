from __future__ import annotations

from typing import Dict

import pandas as pd

from .component import Component


class HydrogenTank(Component):
    """
    Normalized hydrogen storage: `level` in [0, 1], `capacity` total storable mass (kg).
    """

    def __init__(self, capacity_kg: float, initial_level: float) -> None:
        self.capacity = capacity_kg
        self.level = initial_level

    def state(self) -> Dict[str, float]:
        return {"level": self.level}

    def step(self, hydrogen_mass_kg: float, step_timedelta: pd.Timedelta) -> None:
        del step_timedelta  # mass already integrated over the step
        self.level += hydrogen_mass_kg / self.capacity
        if self.level < -1e-9 or self.level > 1.0 + 1e-9:
            raise ValueError(
                f"hydrogen tank level out of bounds: {self.level} (capacity={self.capacity})"
            )
