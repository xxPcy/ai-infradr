from __future__ import annotations

from typing import Any

from ai_infradr.models.issue import Issue, Severity
from ai_infradr.models.snapshot import EnvironmentSnapshot
from ai_infradr.rules import load_rules

from .versioning import version_lt


def _get(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _empty(value: Any) -> bool:
    return value is None or value == ""


def _matches(clause: dict[str, Any], data: dict[str, Any]) -> bool:
    if "all" in clause:
        return all(_matches(child, data) for child in clause["all"])
    if "any" in clause:
        return any(_matches(child, data) for child in clause["any"])

    op = clause["op"]
    value = _get(data, clause.get("path", "")) if "path" in clause else None

    if op == "truthy":
        return bool(value)
    if op == "falsy":
        return not bool(value)
    if op == "empty":
        return _empty(value)
    if op == "not_empty":
        return not _empty(value)
    if op == "gt":
        try:
            return value > clause["value"]
        except TypeError:
            return False
    if op == "version_lt":
        return version_lt(_get(data, clause["left"]), _get(data, clause["right"]))
    if op == "neq_path":
        left = _get(data, clause["left"])
        right = _get(data, clause["right"])
        return left != right
    raise ValueError(f"Unknown rule operator: {op}")


def evaluate_catalog(snapshot: EnvironmentSnapshot) -> list[Issue]:
    data = snapshot.to_dict()
    issues: list[Issue] = []
    for rule in load_rules():
        if not _matches(rule["when"], data):
            continue

        evidence: list[str] = []
        for item in rule.get("evidence", []):
            if "literal" in item:
                value = item["literal"]
            else:
                value = _get(data, item["path"])
                if item.get("optional") and _empty(value):
                    continue
            evidence.append(f"{item['label']}: {value}")

        issues.append(
            Issue(
                code=rule["id"],
                severity=Severity(rule["severity"]),
                title=rule["title"],
                summary=rule["summary"],
                evidence=evidence,
                suggestions=list(rule.get("suggestions", [])),
                references=list(rule.get("references", [])),
                metadata={"rule_schema": "1.0", "source": "catalog.v1.json"},
            )
        )
    return issues
