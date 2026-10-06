from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence

from biocontrolos.process.base.types import Action, ProcessConstraint


@dataclass(frozen=True)
class ConstraintResult:
    valid: bool
    violations: Sequence[str]


class ConstraintEngine(ABC):
    @abstractmethod
    def validate(self, action: Action, constraints: Sequence[ProcessConstraint]) -> ConstraintResult:
        """Validate action feasibility independently of action proposal."""
