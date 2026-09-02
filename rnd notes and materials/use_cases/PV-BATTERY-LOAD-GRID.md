# Use Case: On-Grid Microgrid with PV, Load and Battery

## Objective

Operate an **on-grid** microgrid with **solar**, **load**, **battery** so that optimize (minimaze) grid import, battery cycling and curtailment. The grid assumed as infinite. Forecasts of load and pv are utilized to support control strategy.

## Control design

DNN black box or rule-based or MPC control of pv-load-battery-grid
train DNN black box as evolution strategy (CMA-ES, cross-entropy or other RL algorythm)

## Control variable

battery power

## Metrics
    daily (for weekly take worst day)
    grid import power (integral and peak)
    grid export power (integral and peak)
    battery cycles number
    battery SOC by the end of the day (beafor dark part of the day)
    (battery power smoozness)
