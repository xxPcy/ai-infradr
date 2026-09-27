from __future__ import annotations

from ai_infradr.models.issue import Issue
from ai_infradr.models.snapshot import EnvironmentSnapshot


def build_json_report(snapshot: EnvironmentSnapshot, issues: list[Issue]) -> dict:
    return {
        "snapshot": snapshot.to_dict(),
        "issues": [issue.to_dict() for issue in issues],
        "summary": {
            "issue_count": len(issues),
            "high_or_critical": sum(i.severity.value in {"critical", "high"} for i in issues),
        },
    }
