from __future__ import annotations

import json
from importlib.resources import files

RULE_SCHEMA_VERSION = "1.0"


def load_rules() -> list[dict]:
    resource = files("ai_infradr.rules").joinpath("catalog.v1.json")
    payload = json.loads(resource.read_text(encoding="utf-8"))
    if payload.get("schema_version") != RULE_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported rule schema {payload.get('schema_version')!r}; "
            f"expected {RULE_SCHEMA_VERSION!r}"
        )
    return list(payload.get("rules", []))
