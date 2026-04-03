from typing import Dict
import pandas as pd
from .components import Component
from .time import Time


class Microgrid:

    def __init__(self, time: Time, components: Dict[str, Component]):
        self.timestamp = time.start
        self.step_timedelta = time.step
        self.components = components

    def state(self) -> Dict[str, float]:
        state = {}
        for name, component in self.components.items():
            comp_state = component.state()
            comp_state = {
                name + "_" + param_name: param
                for param_name, param in comp_state.items()
            }
            state.update(comp_state)
        return state

    def step(self, action: Dict[str, float]):
        for name, component in self.components.items():
            if name in action:
                act_for_comp = action[name]
                component.step(act_for_comp, self.step_timedelta)
            else:
                component.step(self.step_timedelta)
