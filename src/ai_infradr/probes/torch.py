from __future__ import annotations

import importlib
import importlib.util

from .base import Probe, ProbeResult


class TorchProbe(Probe):
    name = "torch"

    def available(self) -> bool:
        try:
            return importlib.util.find_spec("torch") is not None
        except (ImportError, AttributeError, ValueError):
            return False

    def collect(self) -> ProbeResult:
        if not self.available():
            return ProbeResult(self.name, {"installed": False})

        try:
            torch = importlib.import_module("torch")
            cuda_available = bool(torch.cuda.is_available())
            device_count = int(torch.cuda.device_count()) if cuda_available else 0
            devices = []
            if cuda_available:
                for index in range(device_count):
                    props = torch.cuda.get_device_properties(index)
                    capability = None
                    try:
                        major, minor = torch.cuda.get_device_capability(index)
                        capability = f"{major}.{minor}"
                    except Exception:  # pragma: no cover - optional runtime detail
                        pass
                    devices.append(
                        {
                            "index": index,
                            "name": props.name,
                            "total_memory_bytes": int(props.total_memory),
                            "compute_capability": capability,
                        }
                    )

            cudnn_version = None
            try:
                if torch.backends.cudnn.is_available():
                    cudnn_version = torch.backends.cudnn.version()
            except Exception:  # pragma: no cover - optional runtime detail
                pass

            data = {
                "installed": True,
                "version": str(torch.__version__),
                "cuda_runtime": getattr(torch.version, "cuda", None),
                "cuda_available": cuda_available,
                "device_count": device_count,
                "devices": devices,
                "cudnn_version": cudnn_version,
            }
            return ProbeResult(self.name, data)
        except Exception as exc:
            return ProbeResult(self.name, {"installed": True}, error=f"{type(exc).__name__}: {exc}")
