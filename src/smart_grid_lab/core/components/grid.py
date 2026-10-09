from typing import Dict

from .component import Component


class Grid(Component):

    def __init__(self):
        self.export_power = 0
        self.import_power = 0

        self.export_limit = 20  # kW
        self.import_limit = 25  # kW

        self.export_limit_violation = 0
        self.import_limit_violation = 0

    def state(self) -> Dict[str, float]:
        return {
            "export_power": self.export_power,
            "import_power": self.import_power,
            "export_limit_violation": self.export_limit_violation,
            "import_limit_violation": self.import_limit_violation,
        }

    def step(self, export_power: float) -> None:
        if export_power >= 0:
            self.export_power = min(self.export_limit, export_power)
            self.export_limit_violation = export_power - self.export_power
            self.import_power = 0
        else:
            self.export_power = 0
            self.import_power = min(self.import_limit, -export_power)
            self.import_limit_violation = -export_power - self.import_power
