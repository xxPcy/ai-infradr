from ai_infradr.diagnosis.rule_engine import evaluate_catalog
from ai_infradr.models.snapshot import EnvironmentSnapshot
from ai_infradr.rules import RULE_SCHEMA_VERSION, load_rules


def test_rule_catalog_loads():
    rules = load_rules()
    assert RULE_SCHEMA_VERSION == "1.0"
    assert rules
    assert len({rule["id"] for rule in rules}) == len(rules)


def test_catalog_emits_evidence_and_source_metadata():
    snapshot = EnvironmentSnapshot(
        system={"os": "Linux"},
        gpu={"available": True, "nvidia_smi": True, "device_count": 1},
        cuda={"toolkit_version": "12.8"},
        torch={
            "installed": True,
            "version": "2.7.1+cu126",
            "cuda_runtime": "12.6",
            "cuda_available": True,
            "device_count": 1,
        },
        nccl={"available": True},
    )
    issues = evaluate_catalog(snapshot)
    issue = next(i for i in issues if i.code == "CUDA_TOOLKIT_DIFFERS_FROM_TORCH_RUNTIME")
    assert issue.evidence == ["nvcc toolkit: 12.8", "torch CUDA runtime: 12.6"]
    assert issue.metadata["source"] == "catalog.v1.json"
