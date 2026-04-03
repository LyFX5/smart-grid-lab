from typing import Dict


class Strategy:

    def action(self) -> Dict[str, float]:
        return {"battery": self.battery_power}

    def step(self, microgrid_state: Dict[str, float]):
        solar_power = microgrid_state["solar_power"]
        load_power = microgrid_state["load_power"]
        remaining_power = solar_power - load_power
        self.battery_power = remaining_power
