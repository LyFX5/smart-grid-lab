from typing import Optional, Dict
import numpy as np
import gymnasium as gym
from .components import Component
from .time import Time
from .microgrid import Microgrid


class MicrogridEnv(gym.Env):

    def __init__(self, time: Time, components: Dict[str, Component]):
        self._microgrid_core = Microgrid(time, components)
        self.observation_space = gym.spaces.Dict(self._microgrid_core.state())
        self.action_space = gym.spaces.Dict()

    def _get_obs(self):
        """Convert internal state to observation format.

        Returns:
            dict: Microgrid components telemetry snap.
        """
        return self._microgrid_core.state()

    def _get_info(self):
        """Compute auxiliary information for debugging.

        here will be info
        """
        return "here will be info"

    def reset(
        self,
        time: Time,
        components: Dict[str, Component],
        seed: Optional[int] = None,
        options: Optional[dict] = None,
    ):
        """Start a new episode.

        Args:
            seed: Random seed for reproducible episodes
            options: Additional configuration (unused in this example)

        Returns:
            tuple: (observation, info) for the initial state
        """
        # IMPORTANT: Must call this first to seed the random number generator
        super().reset(seed=seed)

        self._microgrid_core = Microgrid(time, components)

        observation = self._get_obs()
        info = self._get_info()

        return observation, info

    def step(self, action):
        """Execute one timestep within the environment.

        Args:
            action: gym.spaces.Dict(Dict[str, float])

        Returns:
            tuple: (observation, reward, terminated, truncated, info)
        """

        self._microgrid_core.step(action)

        terminated = ...  # TODO bool

        # We don't use truncation in this simple environment
        # (could add a step limit here if desired)
        truncated = False

        reward = ...  # TODO reward structure

        observation = self._get_obs()
        info = self._get_info()

        return observation, reward, terminated, truncated, info
