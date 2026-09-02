#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 14:12:31 2026

@author: eduard
"""

from typing import Dict

import pandas as pd

from .controller import Controller
from ..forecasting import PVForecastModel, LoadForecastModel


class ForecastsInformedRulesBased(Controller):

    def __init__(
        self, pv_model: PVForecastModel, load_model: LoadForecastModel
    ):
        self.pv_model = pv_model
        self.load_model = load_model

    def action(self) -> Dict[str, float]:
        return {
            "battery": self.battery_power,
            "electrolysers": self.electrolysers_commands,
            "grid": self.grid_power,
        }

    def step(
        self,
        microgrid_state: Dict[str, float],
    ):
        solar_power = microgrid_state["solar_power"]
        load_power = microgrid_state["load_power"]
        battery_soc = microgrid_state["battery_soc"]

        surplus_power = solar_power - load_power

        self.battery_power = surplus_power
        self.electrolysers_commands = [0, 0, 0, 0]
        self.grid_power = 0

        """
        at = ...

        pv_history = ...

        load_history = ...

        pv_forecast: pd.Series = self.pv_model.forecast_pv_kW(pv_history, at)
        load_forecast: pd.Series = self.load_model.forecast_load_kW(
            load_history, at
        )

        ...

        # RULES

        if surplus_power > 0:
            battery_charge_power = self.required_by_battery(
                surplus_power, battery_soc
            )
            surplus_power -= battery_charge_power
        else:
            battery_discharge_power = self.take_from_battery(surplus_power)
            surplus_power += battery_discharge_power
            grid_import_power = self.take_from_grid(surplus_power)
        """
