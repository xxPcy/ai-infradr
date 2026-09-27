from __future__ import annotations

import importlib
import importlib.util

from .base import Probe, ProbeResult


class NCCLProbe(Probe):
    name = "nccl"

    def collect(self) -> ProbeResult:
        try:
            if importlib.util.find_spec("torch") is None:
                return ProbeResult(self.name, {"available": False, "source": None})
            torch = importlib.import_module("torch")
        except Exception as exc:
            return ProbeResult(
                self.name,
                {"available": False},
                error=f"{type(exc).__name__}: {exc}",
            )

        if not getattr(torch, "cuda", None):
            return ProbeResult(self.name, {"available": False, "source": "torch"})

        try:
            nccl = getattr(torch.cuda, "nccl", None)
            if nccl is None or not hasattr(nccl, "version"):
                return ProbeResult(self.name, {"available": False, "source": "torch"})
            version = nccl.version()
            if isinstance(version, tuple):
                version_text = ".".join(str(x) for x in version)
            elif isinstance(version, int):
                major = version // 10000
                minor = (version % 10000) // 100
                patch = version % 100
                version_text = f"{major}.{minor}.{patch}"
            else:
                version_text = str(version)
            return ProbeResult(
                self.name,
                {"available": True, "version": version_text, "source": "torch"},
            )
        except (AttributeError, RuntimeError, OSError):
            # CPU-only / non-NCCL PyTorch builds can expose the Python wrapper
            # while lacking the compiled NCCL symbol. That is absence, not a probe failure.
            return ProbeResult(self.name, {"available": False, "source": "torch"})
        except Exception as exc:
            return ProbeResult(
                self.name,
                {"available": False, "source": "torch"},
                error=f"{type(exc).__name__}: {exc}",
            )
