from __future__ import annotations

import os
import re
from pathlib import Path

from .base import Probe, ProbeResult
from .utils import command_exists, run_command

_NVCC_RELEASE_RE = re.compile(r"release\s+([0-9]+\.[0-9]+)")


class CUDAProbe(Probe):
    name = "cuda"

    def collect(self) -> ProbeResult:
        toolkit_version = None
        nvcc_path = None
        nvcc_error = None

        if command_exists("nvcc"):
            nvcc_path = "nvcc"
            result = run_command(["nvcc", "--version"])
            if result.returncode == 0:
                match = _NVCC_RELEASE_RE.search(result.stdout)
                if match:
                    toolkit_version = match.group(1)
            else:
                nvcc_error = result.stderr or "nvcc --version failed"

        cuda_home = os.environ.get("CUDA_HOME") or os.environ.get("CUDA_PATH")
        if not cuda_home:
            common = Path("/usr/local/cuda")
            if common.exists():
                cuda_home = str(common)

        data = {
            "toolkit_version": toolkit_version,
            "nvcc_available": nvcc_path is not None,
            "nvcc_path": nvcc_path,
            "cuda_home": cuda_home,
            "visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "ld_library_path": os.environ.get("LD_LIBRARY_PATH"),
        }
        return ProbeResult(self.name, data, error=nvcc_error)
