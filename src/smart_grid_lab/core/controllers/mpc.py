#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 12:35:09 2026

@author: eduard
"""

from typing import Dict

from numpy import ndarray

from pandas import Series, Timedelta

import cvxpy as cp

from .forecasts_informed import ForecastsInformed


class MPC(ForecastsInformed):

    def __init__(self, battery_config):
        self.horizon = Timedelta(1, "D")
        self.period = Timedelta(15, "min")
        self.battery_power = 0
        self.battery_config = battery_config

    def action(self) -> Dict[str, float]:
        return {
            "battery": self.battery_power,
        }

    def step(
        self,
        microgrid_state: Dict[str, float],
        forecasts: Dict[str, Series],
    ):

        soc_current = microgrid_state["battery_soc"]

        pv_forecast = forecasts["pv_forecast"]
        load_forecast = forecasts["load_forecast"]
        grid_import_price = forecasts["grid_import_price"]
        grid_export_price = forecasts["grid_export_price"]

        H = int(self.horizon / self.period)
        dt = self.period.total_seconds() / 3600

        # TODO for first value in forecasts use actual current value

        self.battery_power = self.optimize(
            H,
            dt,
            soc_current,
            self.battery_config.max_charge_efficiency,
            self.battery_config.max_discharge_efficiency,
            self.battery_config.capacity_kwh,
            self.battery_config.soc_min,
            self.battery_config.soc_max,
            self.battery_config.max_charge_kw,
            self.battery_config.max_discharge_kw,
            pv_forecast.to_numpy(),
            load_forecast.to_numpy(),
            grid_import_price.to_numpy(),
            grid_export_price.to_numpy(),
        )

    def optimize(
        self,
        H: int,
        dt: float,
        soc_current: float,
        eta_ch: float,
        eta_dis: float,
        E_bat: float,
        soc_min: float,
        soc_max: float,
        p_ch_max: float,
        p_dis_max: float,
        pv_forecast: ndarray,
        load_forecast: ndarray,
        grid_import_price: ndarray,
        grid_export_price: ndarray,
    ):

        p_ch = cp.Variable(H, nonneg=True)
        p_dis = cp.Variable(H, nonneg=True)
        soc = cp.Variable(H + 1)
        p_grid_import = cp.Variable(H, nonneg=True)
        p_grid_export = cp.Variable(H, nonneg=True)

        constraints = [
            soc[0] == soc_current,
            soc[1:]
            == (
                soc[:-1]
                + eta_ch * p_ch * dt / E_bat
                - eta_dis * p_dis * dt / E_bat
            ),
            soc >= soc_min,
            soc <= soc_max,
            p_ch >= 0,
            p_ch <= p_ch_max,
            p_dis >= 0,
            p_dis <= p_dis_max,
            p_grid_import - p_grid_export + pv_forecast + p_dis - p_ch
            == load_forecast,
        ]

        import_cost = cp.sum(
            cp.multiply(grid_import_price, p_grid_import * dt)
        )
        export_cost = cp.sum(
            cp.multiply(grid_export_price, p_grid_export * dt)
        )
        cost = import_cost - export_cost
        # TODO add battery power frequency cost

        problem = cp.Problem(cp.Minimize(cost), constraints)

        problem.solve(solver=cp.OSQP)

        return p_ch.value[0] - p_dis.value[0]

    def __str__(self):
        return "MPC"
