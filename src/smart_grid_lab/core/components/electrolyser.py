#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 20:09:05 2026

@author: eduard
"""

from typing import Dict, Any
import pandas as pd
from enum import Enum

from .component import Component


class StackState(Enum):
    IDLE = 1
    RAMPUP = 2
    STEADY = 3
    RAMPDOWN = 4


class Electrolyser(Component):

    def __init__(self, _id, current_max, temperature_ambient):

        self._id = _id

        # constants
        self.current_max = current_max
        self.temperature_ambient = temperature_ambient
        self.temperature_max = 80
        self.step_min_duration = pd.Timedelta(10, "s")
        self.eps = 0.001

        # variables
        self.pr = 0
        self.pr_reference = 0
        self.stack_state = StackState.IDLE
        self.temperature = self.temperature_ambient  # gradus
        self.degradation = 0
        self.time = pd.Timestamp(0)

        # dynamical parameters
        # TODO identify on some real device data
        self.rampup_inertia = 0.1
        self.steady_inertia = 0.2
        self.rampdown_inertia = 0.3

        self.rampup_treshold = 0.15  # 15%

        self.temperature_rise_inertia = 0.01
        self.temperature_down_inertia = 0.02

        self.degradation_increment = 1

    def current(self):
        # A
        return self.current_max * self.pr

    def voltage(self):
        # V
        return 48  # TODO model VA characteristics

    def power(self):
        # W
        return self.current() * self.voltage()

    def max_power_kW(self):
        pr_saved = self.pr
        self.pr = 1.0
        try:
            return self.power() / 1000.0
        finally:
            self.pr = pr_saved

    def production_efficiency(self):
        # Wh per kg
        return 60

    def hydrogen_production(self):
        # kg per h
        # TODO detilize different dynamics in different states
        return self.power() / self.production_efficiency()

    def state(self) -> Dict[str, Any]:
        return {
            "stack_state": float(self.stack_state.value),
            "production_rate": self.pr,
            "current": self.current(),
            "voltage": self.voltage(),
            "power": self.power(),
            "hydrogen_production": self.hydrogen_production(),
            "temperature": self.temperature,
            "degradation": self.degradation,
        }

    def step(self, pr_reference: float, step_timedelta: pd.Timedelta):
        self.pr_reference = pr_reference
        steps = int(step_timedelta // self.step_min_duration)
        for _ in range(steps):
            if self.stack_state == StackState.IDLE:
                self.idle_dynamics()
            elif self.stack_state == StackState.RAMPUP:
                self.rampup_dynamics()
            elif self.stack_state == StackState.STEADY:
                self.steady_dynamics()
            elif self.stack_state == StackState.RAMPDOWN:
                self.rampdown_dynamics()

    def idle_dynamics(self):
        if self.pr_reference != 0:
            self.stack_state = StackState.RAMPUP
            self.degradation += self.degradation_increment

    def _relax(self, current: float, target: float, inertia: float) -> float:
        """Move a state variable toward a target during one internal sub-step."""
        alpha = min(1.0, max(0.0, inertia))
        return current + alpha * (target - current)

    def rampup_dynamics(self):
        if self.pr_reference <= self.pr:
            self.stack_state = (
                StackState.STEADY
                if self.pr_reference > 0
                else StackState.RAMPDOWN
            )
            return

        self.pr = self._relax(self.pr, self.pr_reference, self.rampup_inertia)
        self.temperature = self._relax(
            self.temperature,
            self.temperature_max,
            self.temperature_rise_inertia,
        )

        remaining = abs(self.pr_reference - self.pr) / max(
            abs(self.pr_reference), self.eps
        )
        if remaining <= self.rampup_treshold:
            self.stack_state = StackState.STEADY

    def steady_dynamics(self):
        diff = self.pr_reference - self.pr
        """
        электролизер реагирует на повышение мощности (Ramp-up) быстрее, 
        чем на понижение (Ramp-down), 
        из-за динамики давления газов и тепловых процессов
        """
        inertia = self.steady_inertia * (2 if diff < 0 else 4)
        self.pr = self._relax(self.pr, self.pr_reference, inertia)
        self.temperature = self._relax(
            self.temperature,
            self.temperature_max,
            self.temperature_rise_inertia,
        )

        if self.pr_reference == 0:
            self.stack_state = StackState.RAMPDOWN

    def rampdown_dynamics(self):
        self.pr = self._relax(
            self.pr, self.pr_reference, self.rampdown_inertia
        )
        self.temperature = self._relax(
            self.temperature,
            self.temperature_ambient,
            self.temperature_down_inertia,
        )

        if abs(self.pr) < self.eps:
            self.pr = 0.0
            self.stack_state = StackState.IDLE
            self.degradation += self.degradation_increment
