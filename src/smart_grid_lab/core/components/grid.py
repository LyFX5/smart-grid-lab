#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 15:35:49 2026

@author: eduard
"""

from typing import Dict

from .component import Component


class Grid(Component):

    def __init__(self):
        self.import_power = 0
        self.export_power = 0

    def state(self) -> Dict[str, float]:
        return {
            "import_power": self.import_power,
            "export_power": self.export_power,
        }

    def step(self, power: float) -> None:
        if power >= 0:
            self.export_power = power
            self.import_power = 0
        else:
            self.export_power = 0
            self.import_power = -power


class GridLimited(Grid):

    def __init__(self, export_limit, import_limit):
        super(GridLimited, self).__init__()
        self.export_limit = export_limit
        self.import_limit = import_limit
        self.dump = 0
        self.exceed = 0

    def step(self, power: float) -> None:
        if power >= 0:
            self.export_power = min(self.export_limit, power)
            self.dump = power - self.export_power
            self.import_power = 0
        else:
            self.export_power = 0
            self.import_power = min(self.import_limit, -power)
            self.exceed = -power - self.import_power
