from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from .components import Component


class Microgrid:
    """
    Coordinates component stepping for one microgrid timestep.

    Known components are stepped in a fixed order so power devices and the
    hydrogen balance stay consistent. ``hydrogen_tank`` is fed from
    ``electrolyser`` production over the step (not via the action dict).
    """

    _ORDER_FIRST = ("solar", "load", "battery", "electrolyser")

    def __init__(self, time, components: Dict[str, Component]):
        self.timestamp = time.start
        self.step_timedelta = time.step
        self.components = components

    def state(self) -> Dict[str, Any]:
        state: Dict[str, Any] = {}
        for name, component in self.components.items():
            comp_state = component.state()
            for param_name, param in comp_state.items():
                key = f"{name}_{param_name}"
                if isinstance(param, pd.Timestamp):
                    state[key] = param
                else:
                    state[key] = float(param)
        return state

    def step(self, action: Dict[str, float]) -> None:
        dt = self.step_timedelta
        components = self.components

        for name in self._ORDER_FIRST:
            if name not in components:
                continue
            c = components[name]
            if name in ("solar", "load"):
                c.step(dt)
            elif name == "battery":
                c.step(float(action.get("battery", 0.0)), dt)
            elif name == "electrolyser":
                c.step(float(action.get("electrolyser", 0.0)), dt)

        if (
            "hydrogen_tank" in components and "electrolyser" in components
        ):  # TODO electrolyser_ ...
            ely = components["electrolyser"]
            tank = components["hydrogen_tank"]
            dt_h = dt.total_seconds() / 3600.0
            mass_kg = ely.hydrogen_production() * dt_h
            tank.step(mass_kg, dt)

        handled = set(self._ORDER_FIRST) | {"hydrogen_tank"}
        for name, component in components.items():
            if name in handled:
                continue
            if not hasattr(component, "step"):
                continue
            if name in action:
                component.step(action[name], dt)
            else:
                component.step(dt)
