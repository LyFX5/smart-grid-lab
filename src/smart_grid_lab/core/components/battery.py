from typing import Dict
import pandas as pd
import numpy as np
from .component import Component


"""
Если вы проигнорируете эту нелинейность, ваша стратегия управления решит, 
что может "запихнуть" последние 5% энергии в АКБ так же быстро, как и первые 50%. 
В реальности это займет в 3-4 раза больше времени.

Если в это время дует сильный ветер, а АКБ уже "не принимает" энергию из-за SoC>90%, 
ваша система должна мгновенно перебросить этот избыток на AEM-электролизеры. 
Без учета нелинейности АКБ вы получите ложноположительный результат в симуляции, 
а в поле — сброс энергии (curtailment) или аварию.

«безопасное плато» (обычно в диапазоне 20–80% SoC), 
где АКБ работает линейно и эффективно
"""


class Battery(Component):

    def __init__(
        self,
        capacity_kwh,
        max_charge_kw,
        max_discharge_kw,
        max_charge_efficiency,
        max_discharge_efficiency,
        initial_soc,
    ):
        self.capacity_kwh = capacity_kwh

        self.max_charge_kw = max_charge_kw
        self.max_discharge_kw = max_discharge_kw

        self.max_charge_efficiency = max_charge_efficiency
        self.max_discharge_efficiency = max_discharge_efficiency

        self.soc = initial_soc
        self.soc_max = 1
        self.soc_min = 0.05

        self.available_power = 0
        self.charge_power = 0
        self.discharge_power = 0

    def state(self) -> Dict[str, float]:
        return {
            "available_power": self.available_power,
            "charge_power": self.charge_power,
            "discharge_power": self.discharge_power,
            "soc": self.soc,
        }

    def efficiency(self, soc: float, is_charging: bool):
        if is_charging:
            alpha = 0.1
            betha = 10
            return self.max_charge_efficiency * (1 - alpha * np.exp(betha * (soc - 1)))
        alpha = 0.1  # TODO in constructor (might be different in advanced models)
        betha = 10
        return self.max_discharge_efficiency * (1 - alpha * np.exp(betha * (soc - 1)))

    def power_limit(self, soc: float, is_charging: bool):

        tau = 0.1
        """
        (обычно в диапазоне 0.05 – 0.1 для Li-ion).
        Чем меньше τ, тем позже начинается снижение мощности.
        """

        gamma = 0.05
        """
        (обычно 0.02 – 0.05). 
        Разряд обычно ограничивается более резко и «позже», чем заряд.
        """

        if is_charging:
            arg = (soc - self.soc_max) / tau
            return self.max_charge_kw * (1 - np.exp(arg))
        arg = (self.soc_min - soc) / gamma
        return self.max_discharge_kw * (1 - np.exp(arg))

    def step(self, power: float, step_timedelta: pd.Timedelta):

        self.available_power = power
        step_hours = step_timedelta.total_seconds() / 3600
        is_charging = power > 0
        efficiency = self.efficiency(self.soc, is_charging)
        power_limit = self.power_limit(self.soc, is_charging)

        if is_charging:
            self.charge_power = min(power_limit, power)
            self.discharge_power = 0
            energy_delta = self.charge_power * step_hours * efficiency
        else:
            self.charge_power = 0
            self.discharge_power = min(power_limit, -power)
            energy_delta = -self.discharge_power * step_hours * efficiency

        self.soc += energy_delta / self.capacity_kwh
