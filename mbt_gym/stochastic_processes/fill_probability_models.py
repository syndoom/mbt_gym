import abc
from typing import Optional

import numpy as np

from mbt_gym.stochastic_processes.StochasticProcessModel import StochasticProcessModel


class FillProbabilityModel(StochasticProcessModel):
    def __init__(
        self,
        min_value: np.ndarray,
        max_value: np.ndarray,
        step_size: float,
        terminal_time: float,
        initial_state: np.ndarray,
        num_trajectories: int = 1,
        seed: int = None,
    ):
        super().__init__(min_value, max_value, step_size, terminal_time, initial_state, num_trajectories, seed)

    @abc.abstractmethod
    def _get_fill_probabilities(self, depths: np.ndarray) -> np.ndarray:
        """Note that _get_fill_probabilities can return a 'probability' greater than one. However, this is not an issue
        for it is only use is in `get_hypothetical_fills` below."""
        pass

    def get_fills(self, depths: np.ndarray) -> np.ndarray:
        assert depths.shape == (self.num_trajectories, 2), (
            "Depths must be a numpy array of shape "
            + f"({self.num_trajectories},2). Instead it is a numpy array of shape {depths.shape}."
        )
        unif = self.rng.uniform(size=(self.num_trajectories, 2))
        return unif < self._get_fill_probabilities(depths)

    @property
    @abc.abstractmethod
    def max_depth(self) -> float:
        pass


class ExponentialFillFunction(FillProbabilityModel):
    def __init__(
        self, fill_exponent: float = 1.5, step_size: float = 0.1, num_trajectories: int = 1, seed: Optional[int] = None
    ):
        self.fill_exponent = fill_exponent
        super().__init__(
            min_value=np.array([[]]),
            max_value=np.array([[]]),
            step_size=step_size,
            terminal_time=0.0,
            initial_state=np.array([[]]),
            num_trajectories=num_trajectories,
            seed=seed,
        )

    def _get_fill_probabilities(self, depths: np.ndarray) -> np.ndarray:
        return np.exp(-self.fill_exponent * depths)

    @property
    def max_depth(self) -> float:
        return -np.log(0.01) / self.fill_exponent

    def update(self, arrivals: np.ndarray, fills: np.ndarray, actions: np.ndarray):
        pass


class TriangularFillFunction(FillProbabilityModel):
    def __init__(
        self, max_fill_depth: float = 1.0, step_size: float = 0.1, num_trajectories: int = 1, seed: Optional[int] = None
    ):
        self.max_fill_depth = max_fill_depth
        super().__init__(
            min_value=np.array([[]]),
            max_value=np.array([[]]),
            step_size=step_size,
            terminal_time=0.0,
            initial_state=np.array([[]]),
            num_trajectories=num_trajectories,
            seed=seed,
        )

    def _get_fill_probabilities(self, depths: np.ndarray) -> np.ndarray:
        return np.max(1 - np.max(depths, 0) / self.max_fill_depth, 0)

    @property
    def max_depth(self) -> float:
        return 1.5 * self.max_fill_depth

    def update(self, arrivals: np.ndarray, fills: np.ndarray, actions: np.ndarray):
        pass


class PowerFillFunction(FillProbabilityModel):
    def __init__(
        self,
        fill_exponent: float = 1.5,
        fill_multiplier: float = 1.5,
        step_size: float = 0.1,
        num_trajectories: int = 1,
        seed: Optional[int] = None,
    ):
        self.fill_exponent = fill_exponent
        self.fill_multiplier = fill_multiplier
        super().__init__(
            min_value=np.array([[]]),
            max_value=np.array([[]]),
            step_size=step_size,
            terminal_time=0.0,
            initial_state=np.array([[]]),
            num_trajectories=num_trajectories,
            seed=seed,
        )

    def _get_fill_probabilities(self, depths: np.ndarray) -> np.ndarray:
        return (1 + (self.fill_multiplier * np.max(depths, 0)) ** self.fill_exponent) ** -1

    @property
    def max_depth(self) -> float:
        return 0.01 ** (-1 / self.fill_exponent) - 1

    def update(self, arrivals: np.ndarray, fills: np.ndarray, actions: np.ndarray):
        pass
