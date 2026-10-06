from dataclasses import dataclass


@dataclass(frozen=True)
class SupervisoryConstraint:
    constraint_type: str
    subject: str
    parameter: str
    maximum: float | None
    minimum: float | None
    reason: str
    confidence: float
    requires_human_confirmation: bool
