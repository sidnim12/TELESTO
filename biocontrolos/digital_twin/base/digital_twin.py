from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence

from biocontrolos.core.state import ProcessState
from biocontrolos.process.base import Action


@dataclass(frozen=True)
class TrajectoryPrediction:
    states: Sequence[ProcessState]
    uncertainty: float | None = None


class DigitalTwin(ABC):
    @abstractmethod
    def simulate(self, initial_state: ProcessState, actions: Sequence[Action]) -> TrajectoryPrediction: ...

    @abstractmethod
    def predict_next_state(self, state: ProcessState, action: Action) -> ProcessState: ...

    @abstractmethod
    def estimate_uncertainty(self, prediction: TrajectoryPrediction) -> float: ...
