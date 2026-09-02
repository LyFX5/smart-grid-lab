#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 14:36:25 2026

@author: eduard
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class Controller(ABC):

    @abstractmethod
    def action(self) -> Dict: ...

    @abstractmethod
    def step(self, state: Any) -> None: ...
