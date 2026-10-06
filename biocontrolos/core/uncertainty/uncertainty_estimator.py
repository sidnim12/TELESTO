from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping

from biocontrolos.core.state import BeliefState


@dataclass(frozen=True)
class UncertaintyEstimate:
    values: Mapping[str, float]
    calibrated: bool


class UncertaintyEstimator(ABC):
    @abstractmethod
    def estimate(self, belief: BeliefState) -> UncertaintyEstimate:
        """Quantify uncertainty; calibration is a testable requirement."""
