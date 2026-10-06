from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum

from biocontrolos.process.base import Action


class SafetyStatus(StrEnum):
    EXECUTE = "execute"
    MODIFY = "modify"
    REJECT = "reject"
    REQUIRE_HUMAN_APPROVAL = "require_human_approval"


@dataclass(frozen=True)
class SafetyDecision:
    status: SafetyStatus
    reason: str
    action: Action | None = None


class SafetyGate(ABC):
    """Final independent authorization boundary for every action."""

    @abstractmethod
    def evaluate(self, action: Action) -> SafetyDecision: ...
