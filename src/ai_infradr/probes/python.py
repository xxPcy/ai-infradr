from __future__ import annotations

import os
import platform
import sys

from .base import Probe, ProbeResult


class PythonProbe(Probe):
    name = "python"

    def collect(self) -> ProbeResult:
        implementation = platform.python_implementation()
        data = {
            "version": platform.python_version(),
            "implementation": implementation,
            "executable": sys.executable,
            "prefix": sys.prefix,
            "base_prefix": sys.base_prefix,
            "virtual_env": os.environ.get("VIRTUAL_ENV"),
            "conda_prefix": os.environ.get("CONDA_PREFIX"),
            "is_venv": sys.prefix != sys.base_prefix,
        }
        return ProbeResult(self.name, data)
