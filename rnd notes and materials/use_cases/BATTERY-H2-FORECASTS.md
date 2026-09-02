# Use Case: Forecast-Based Hydrogen Production Control

## Objective

Operate a microgrid with **solar**, **load**, **battery** and **h2 system** so that optimize (minimaze) grid import, battery cycling, curtailment and h2 metrics. The grid assumed as infinite. Forecasts of load and pv are utilized to support control strategy.

## Control design

rule-based
or MPC
or DNN (black box)

train DNN black box as evolution strategy (CMA-ES, cross-entropy)
or other RL algorithm

## Control variable

battery power
electrolysers production rates

## Metrics
    daily (for weekly take worst day)
    grid import power (integral and peak)
    grid export power (integral and peak)
    battery cycles number
    battery SOC by the end of the day (beafor dark part of the day)
    (battery power smoozness)
    battery mismatch: available against actual
    electrolysers cycles
    h2 level (TODO at wich point?)
    h2 power mismatch: available against actual

