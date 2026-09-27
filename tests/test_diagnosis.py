from ai_infradr.diagnosis import DiagnosisEngine
from ai_infradr.models.snapshot import EnvironmentSnapshot


def codes(snapshot: EnvironmentSnapshot) -> set[str]:
    return {issue.code for issue in DiagnosisEngine().diagnose(snapshot)}


def base_snapshot() -> EnvironmentSnapshot:
    return EnvironmentSnapshot(
        system={"os": "Linux", "release": "6.8"},
        python={"version": "3.11.9"},
        gpu={
            "available": True,
            "nvidia_smi": True,
            "device_count": 2,
            "driver_version": "570.86",
            "driver_cuda_supported": "12.8",
            "devices": [{"name": "NVIDIA A800"}, {"name": "NVIDIA A800"}],
        },
        cuda={"toolkit_version": "12.6", "visible_devices": None},
        torch={
            "installed": True,
            "version": "2.7.1+cu126",
            "cuda_runtime": "12.6",
            "cuda_available": True,
            "device_count": 2,
        },
        nccl={"available": True, "version": "2.26.2"},
    )


def test_healthy_snapshot_has_no_compatibility_issue():
    assert codes(base_snapshot()) == set()


def test_old_driver_is_high_issue():
    snapshot = base_snapshot()
    snapshot.gpu["driver_cuda_supported"] = "12.4"
    assert "NVIDIA_DRIVER_TOO_OLD_FOR_TORCH_CUDA" in codes(snapshot)


def test_cuda_toolkit_difference_is_low_signal_not_hard_failure():
    snapshot = base_snapshot()
    snapshot.cuda["toolkit_version"] = "12.8"
    issues = DiagnosisEngine().diagnose(snapshot)
    issue = next(item for item in issues if item.code == "CUDA_TOOLKIT_DIFFERS_FROM_TORCH_RUNTIME")
    assert issue.severity.value == "low"


def test_cpu_only_torch_on_gpu_machine():
    snapshot = base_snapshot()
    snapshot.torch.update({"cuda_runtime": None, "cuda_available": False, "device_count": 0})
    assert "PYTORCH_CPU_ONLY_WITH_NVIDIA_GPU" in codes(snapshot)


def test_nccl_missing_on_multi_gpu():
    snapshot = base_snapshot()
    snapshot.nccl = {"available": False}
    assert "NCCL_UNAVAILABLE_FOR_MULTI_GPU" in codes(snapshot)


def test_visibility_mismatch_respects_cuda_visible_devices():
    snapshot = base_snapshot()
    snapshot.cuda["visible_devices"] = "0"
    snapshot.torch["device_count"] = 1
    issues = DiagnosisEngine().diagnose(snapshot)
    issue = next(item for item in issues if item.code == "GPU_VISIBILITY_DIFFERS")
    assert issue.severity.value == "info"
