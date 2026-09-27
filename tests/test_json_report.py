from ai_infradr.models.issue import Issue, Severity
from ai_infradr.models.snapshot import EnvironmentSnapshot
from ai_infradr.reports.json_report import build_json_report


def test_json_report_is_serializable_shape():
    snapshot = EnvironmentSnapshot(system={"os": "Linux"})
    issue = Issue(
        code="X",
        severity=Severity.HIGH,
        title="Example",
        summary="Example issue",
    )
    report = build_json_report(snapshot, [issue])
    assert report["issues"][0]["severity"] == "high"
    assert report["summary"]["high_or_critical"] == 1
