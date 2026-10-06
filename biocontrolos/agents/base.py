from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class AgentRecommendation:
    recommendation_type: str
    payload: Mapping[str, object]
    requires_safety_review: bool = True


class Agent(ABC):
    @abstractmethod
    def recommend(self, context: Mapping[str, object]) -> AgentRecommendation: ...
