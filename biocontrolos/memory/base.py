from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class BatchRecord:
    batch_id: str
    outcomes: Mapping[str, float | str]
    human_overrides: Sequence[str]


class MemoryStore(ABC):
    @abstractmethod
    def save_batch(self, record: BatchRecord) -> None: ...

    @abstractmethod
    def query_batches(self, criteria: Mapping[str, object]) -> Sequence[BatchRecord]: ...
