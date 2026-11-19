#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 12:35:09 2026

@author: eduard
"""

from typing import Dict

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
        price_forecast = forecasts["price_forecast"]

        H = int(self.horizon / self.period)
        dt = self.period.total_seconds() / 3600

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
            pv_forecast,
            load_forecast,
            price_forecast,
        )

    def optimize(
        self,
        H,
        dt,
        soc_current,
        eta_ch,
        eta_dis,
        E_bat,
        soc_min,
        soc_max,
        p_ch_max,
        p_dis_max,
        pv_forecast,
        load_forecast,
        price_forecast,
    ):

        p_ch = cp.Variable(H, nonneg=True)
        p_dis = cp.Variable(H, nonneg=True)
        soc = cp.Variable(H + 1)
        p_grid = cp.Variable(H, nonneg=True)

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
            p_ch <= p_ch_max,
            p_dis <= p_dis_max,
            p_grid + pv_forecast + p_dis - p_ch == load_forecast,
        ]

        cost = cp.sum(price_forecast * p_grid * dt)

        problem = cp.Problem(cp.Minimize(cost), constraints)

        problem.solve(solver=cp.OSQP)

        return p_dis.value[0] - p_ch.value[0]
