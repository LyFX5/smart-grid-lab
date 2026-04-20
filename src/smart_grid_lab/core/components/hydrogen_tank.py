#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 23:50:00 2026

@author: eduard
"""


class HydrogenTank:

    def __init__(self, capacity, init_level):

        self.capacity = capacity
        self.level = init_level

    def state(self):
        return {"level": self.level}

    def step(self, hydrogen_income):
        self.level += hydrogen_income / self.capacity
        assert 0 <= self.level <= 1
