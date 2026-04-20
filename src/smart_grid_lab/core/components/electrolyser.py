#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 20:09:05 2026

@author: eduard
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from .component import Component
from enum import Enum


class StackState(Enum):
    IDLE = 1
    RAMPUP = 2
    STEADY = 3
    RAMPDOWN = 4


class Electrolyser:

    def __init__(self, current_max, temperature_ambient):

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
        self.time = pd.Timestamp()

        # dynamical parameters
        # TODO
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

    def production_efficiency(self):
        # Wh per kg
        return 60

    def hydrogen_production(self):
        # kg per h
        # TODO detilize different dynamics in different states
        return self.power() / self.production_efficiency()

    def state(self) -> Dict[str, Any]:
        return {
            "stack_state": self.stack_state,
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

    def rampup_dynamics(self):
        diff = self.pr_reference - self.pr
        self.pr += self.step_min_duration * self.rampup_inertia * diff

        temperature_diff = self.temperature_max - self.temperature
        self.temperature += (
            self.step_min_duration * self.temperature_rise_inertia * temperature_diff
        )

        assert diff > 0

        if abs(diff / self.pr_reference - self.rampup_treshold) < self.eps:
            self.stack_state = StackState.STEADY

    def steady_dynamics(self):
        diff = self.pr_reference - self.pr
        """
        электролизер реагирует на повышение мощности (Ramp-up) быстрее, 
        чем на понижение (Ramp-down), 
        из-за динамики давления газов и тепловых процессов
        """
        inertia = self.steady_inertia * (2 if diff < 0 else 4)
        self.pr += self.step_min_duration * inertia * diff

        temperature_diff = self.temperature_max - self.temperature
        self.temperature += (
            self.step_min_duration * self.temperature_rise_inertia * temperature_diff
        )

        if self.pr_reference == 0:
            self.stack_state = StackState.RAMPDOWN

    def rampdown_dynamics(self):
        diff = self.pr_reference - self.pr
        self.pr += self.step_min_duration * self.rampdown_inertia * diff

        temperature_diff = self.temperature_ambient - self.temperature
        self.temperature += (
            self.step_min_duration * self.temperature_down_inertia * temperature_diff
        )

        if abs(self.pr) < self.eps:
            self.stack_state = StackState.IDLE
            self.degradation += self.degradation_increment
