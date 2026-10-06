from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping


@dataclass(frozen=True)
class ProcessState:
    """State representation; synthetic or process adapters define its variables."""

    values: Mapping[str, float]
    timestamp: datetime


@dataclass(frozen=True)
class Observation:
    values: Mapping[str, float | None]
    timestamp: datetime
    source: str


@dataclass(frozen=True)
class BeliefState:
    mean: Mapping[str, float]
    uncertainty: Mapping[str, float]
    timestamp: datetime
    metadata: Mapping[str, str] = field(default_factory=dict)
