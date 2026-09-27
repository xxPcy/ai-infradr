from __future__ import annotations

import os
import platform

from .base import Probe, ProbeResult


class SystemProbe(Probe):
    name = "system"

    def collect(self) -> ProbeResult:
        libc_name, libc_version = platform.libc_ver()
        data = {
            "os": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "platform": platform.platform(),
            "libc": libc_name or None,
            "libc_version": libc_version or None,
            "hostname": platform.node(),
            "container_hint": self._container_hint(),
        }
        return ProbeResult(self.name, data)

    @staticmethod
    def _container_hint() -> str | None:
        if os.path.exists("/.dockerenv"):
            return "docker"
        try:
            with open("/proc/1/cgroup", encoding="utf-8") as handle:
                text = handle.read().lower()
            if "docker" in text:
                return "docker"
            if "kubepods" in text:
                return "kubernetes"
            if "containerd" in text:
                return "containerd"
        except OSError:
            pass
        return None
