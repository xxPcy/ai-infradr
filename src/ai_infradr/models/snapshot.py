from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

SNAPSHOT_SCHEMA_VERSION = "1.0"


@dataclass
class EnvironmentSnapshot:
    schema_version: str = SNAPSHOT_SCHEMA_VERSION
    collected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    system: dict[str, Any] = field(default_factory=dict)
    python: dict[str, Any] = field(default_factory=dict)
    gpu: dict[str, Any] = field(default_factory=dict)
    cuda: dict[str, Any] = field(default_factory=dict)
    torch: dict[str, Any] = field(default_factory=dict)
    nccl: dict[str, Any] = field(default_factory=dict)
    probe_errors: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
