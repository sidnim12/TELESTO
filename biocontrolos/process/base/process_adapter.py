from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence

from biocontrolos.core.rewards import RewardOutcome
from biocontrolos.core.state import Observation, ProcessState

from .types import Action, ProcessConstraint


class ProcessAdapter(ABC):
    """Exclusive process boundary for the reusable autonomy engine."""

    @abstractmethod
    def get_state(self) -> ProcessState: ...

    @abstractmethod
    def get_observation(self) -> Observation: ...

    @abstractmethod
    def available_actions(self) -> Sequence[Action]: ...

    @abstractmethod
    def transition_model(self, action: Action) -> ProcessState: ...

    @abstractmethod
    def get_constraints(self) -> Sequence[ProcessConstraint]: ...

    @abstractmethod
    def get_quality_attributes(self) -> Mapping[str, float]: ...

    @abstractmethod
    def calculate_reward(self) -> RewardOutcome: ...

    @abstractmethod
    def estimate_process_risk(self, action: Action) -> float: ...

    @abstractmethod
    def get_sensor_definitions(self) -> Mapping[str, Mapping[str, object]]: ...

    @abstractmethod
    def get_actuator_definitions(self) -> Mapping[str, Mapping[str, object]]: ...

    @abstractmethod
    def get_measurement_costs(self) -> Mapping[str, float]: ...

    @abstractmethod
    def get_experiment_options(self) -> Sequence[Mapping[str, object]]: ...

    @abstractmethod
    def validate_action(self, action: Action) -> bool: ...
