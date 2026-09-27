from __future__ import annotations

import re

from .base import Probe, ProbeResult
from .utils import command_exists, run_command

_CUDA_RE = re.compile(r"CUDA Version\s*:?\s*([0-9]+(?:\.[0-9]+)*)")


def _parse_cuda_supported(output: str) -> str | None:
    match = _CUDA_RE.search(output)
    if match:
        return match.group(1)
    return None


def _collect_driver_cuda_supported() -> str | None:
    for args in (["nvidia-smi", "--version"], ["nvidia-smi"]):
        result = run_command(args)
        if result.returncode != 0:
            continue
        cuda_supported = _parse_cuda_supported(result.stdout)
        if cuda_supported:
            return cuda_supported
    return None


class GPUProbe(Probe):
    name = "gpu"

    def available(self) -> bool:
        return command_exists("nvidia-smi")

    def collect(self) -> ProbeResult:
        if not self.available():
            return ProbeResult(
                self.name,
                {
                    "vendor": "nvidia",
                    "available": False,
                    "device_count": 0,
                    "devices": [],
                    "nvidia_smi": False,
                },
            )

        query = run_command(
            [
                "nvidia-smi",
                "--query-gpu=index,name,driver_version,memory.total",
                "--format=csv,noheader,nounits",
            ]
        )
        if query.returncode != 0:
            return ProbeResult(
                self.name,
                {"vendor": "nvidia", "available": False, "nvidia_smi": True},
                error=query.stderr or "nvidia-smi failed",
            )

        devices = []
        for line in query.stdout.splitlines():
            parts = [part.strip() for part in line.split(",", 3)]
            if len(parts) != 4:
                continue
            index, name, driver_version, memory_total = parts
            try:
                memory_mib = int(float(memory_total))
            except ValueError:
                memory_mib = None
            devices.append(
                {
                    "index": int(index) if index.isdigit() else index,
                    "name": name,
                    "driver_version": driver_version,
                    "memory_total_mib": memory_mib,
                }
            )

        cuda_supported = _collect_driver_cuda_supported()

        driver_versions = sorted({d["driver_version"] for d in devices if d["driver_version"]})
        return ProbeResult(
            self.name,
            {
                "vendor": "nvidia",
                "available": bool(devices),
                "nvidia_smi": True,
                "device_count": len(devices),
                "devices": devices,
                "driver_version": (
                    driver_versions[0] if len(driver_versions) == 1 else driver_versions
                ),
                "driver_cuda_supported": cuda_supported,
            },
        )
