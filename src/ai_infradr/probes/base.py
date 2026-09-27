from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProbeResult:
    name: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class Probe(ABC):
    name: str

    def available(self) -> bool:
        return True

    @abstractmethod
    def collect(self) -> ProbeResult:
        raise NotImplementedError
