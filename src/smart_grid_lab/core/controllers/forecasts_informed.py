#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 10:48:35 2026

@author: eduard
"""

from abc import abstractmethod
from typing import Dict, Any
from pandas import Series
from .controller import Controller


class ForecastsInformed(Controller):

    @abstractmethod
    def action(self) -> Dict: ...

    @abstractmethod
    def step(
        self, state: Dict[str, Any], forecasts: Dict[str, Series]
    ) -> None: ...
