from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class RewardOutcome:
    objectives: Mapping[str, float]
    scalar_reward: float | None = None


class RewardModel(ABC):
    @abstractmethod
    def evaluate(self, outcomes: Mapping[str, float]) -> RewardOutcome:
        """Support process-supplied objectives and optional scalarization."""
