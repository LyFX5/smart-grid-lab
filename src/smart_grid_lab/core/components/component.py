from abc import ABC, abstractmethod
from pandas import Timedelta
from typing import Dict, Any


class Component(ABC):

    @abstractmethod
    def state(self) -> Dict: ...

    @abstractmethod
    def step(self, control: Any, dt: Timedelta) -> None: ...
