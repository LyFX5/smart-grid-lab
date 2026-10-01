# Use Case: Microgrid of PV, Load and Battery

## Objective

Operate a microgrid of **PV**, **Load**, **Battery**
Optimize (minimaze) grid import, battery cycling, curtailment / grid import

## Control design

Reactive

## Control variable

battery power

## Metrics daily (for weekly take worst day)
    battery cycles number
    battery SOC by the end of the day (beafor dark part of the day)
    (battery power smoozness)
    remaining power. surpluse or deficite
        grid import power (integral and peak)
        grid export power (integral and peak)
