from ai_infradr.cli.main import _should_fail
from ai_infradr.models.issue import Issue, Severity


def issue(severity: Severity) -> Issue:
    return Issue(code="X", severity=severity, title="x", summary="x")


def test_fail_on_thresholds():
    assert _should_fail([issue(Severity.HIGH)], "high") is True
    assert _should_fail([issue(Severity.MEDIUM)], "high") is False
    assert _should_fail([issue(Severity.MEDIUM)], "medium") is True
    assert _should_fail([issue(Severity.CRITICAL)], "medium") is True
    assert _should_fail([issue(Severity.CRITICAL)], "never") is False
