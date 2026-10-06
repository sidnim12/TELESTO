from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping


class ActionKind(StrEnum):
    CONTROL = "control"
    MEASURE = "measure"
    EXPERIMENT = "experiment"
    SIMULATE = "simulate"
    WAIT = "wait"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class Action:
    kind: ActionKind
    values: Mapping[str, float | str] = field(default_factory=dict)
    rationale: str = ""


@dataclass(frozen=True)
class ProcessConstraint:
    name: str
    description: str
    hard: bool = True
