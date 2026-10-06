from abc import ABC, abstractmethod
from typing import Sequence

from .models import BeliefState, Observation


class StateEstimator(ABC):
    """Pluggable estimator for partially observed process state."""

    @abstractmethod
    def estimate(self, observation: Observation, history: Sequence[Observation]) -> BeliefState:
        """Return a belief state without assuming a particular filtering method."""
