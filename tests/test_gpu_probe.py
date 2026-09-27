from ai_infradr.probes import gpu as gpu_module
from ai_infradr.probes.gpu import GPUProbe
from ai_infradr.probes.utils import CommandResult


def test_gpu_probe_parses_nvidia_smi(monkeypatch):
    monkeypatch.setattr(gpu_module, "command_exists", lambda name: True)

    def fake_run(args, timeout=5.0):
        if "--query-gpu=index,name,driver_version,memory.total" in args:
            return CommandResult(
                0,
                "0, NVIDIA A800, 570.86, 81920\n1, NVIDIA A800, 570.86, 81920",
                "",
            )
        return CommandResult(
            0,
            "NVIDIA-SMI version  : 570.86\nCUDA Version        : 12.8",
            "",
        )

    monkeypatch.setattr(gpu_module, "run_command", fake_run)
    result = GPUProbe().collect()
    assert result.error is None
    assert result.data["device_count"] == 2
    assert result.data["driver_version"] == "570.86"
    assert result.data["driver_cuda_supported"] == "12.8"


def test_gpu_probe_falls_back_to_summary_for_driver_cuda(monkeypatch):
    monkeypatch.setattr(gpu_module, "command_exists", lambda name: True)

    def fake_run(args, timeout=5.0):
        if "--query-gpu=index,name,driver_version,memory.total" in args:
            return CommandResult(0, "0, NVIDIA A800, 570.86, 81920", "")
        if args == ["nvidia-smi", "--version"]:
            return CommandResult(127, "", "timed out")
        return CommandResult(
            0,
            "NVIDIA-SMI 570.86   Driver Version: 570.86   CUDA Version: 12.8",
            "",
        )

    monkeypatch.setattr(gpu_module, "run_command", fake_run)
    result = GPUProbe().collect()
    assert result.error is None
    assert result.data["driver_cuda_supported"] == "12.8"
