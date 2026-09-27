from __future__ import annotations

from ai_infradr.diagnosis import DiagnosisEngine
from ai_infradr.models.issue import Issue
from ai_infradr.models.snapshot import EnvironmentSnapshot
from ai_infradr.probes import (
    CUDAProbe,
    GPUProbe,
    NCCLProbe,
    Probe,
    PythonProbe,
    SystemProbe,
    TorchProbe,
)


class InfraDr:
    def __init__(
        self,
        probes: list[Probe] | None = None,
        engine: DiagnosisEngine | None = None,
    ) -> None:
        self.probes = probes or [
            SystemProbe(),
            PythonProbe(),
            GPUProbe(),
            CUDAProbe(),
            TorchProbe(),
            NCCLProbe(),
        ]
        self.engine = engine or DiagnosisEngine()

    def snapshot(self) -> EnvironmentSnapshot:
        snapshot = EnvironmentSnapshot()
        for probe in self.probes:
            try:
                result = probe.collect()
            except Exception as exc:  # defensive boundary for third-party/future probes
                snapshot.probe_errors[probe.name] = f"{type(exc).__name__}: {exc}"
                continue
            setattr(snapshot, probe.name, result.data)
            if result.error:
                snapshot.probe_errors[probe.name] = result.error
        return snapshot

    def diagnose(self) -> tuple[EnvironmentSnapshot, list[Issue]]:
        snapshot = self.snapshot()
        return snapshot, self.engine.diagnose(snapshot)


def run_diagnosis() -> tuple[EnvironmentSnapshot, list[Issue]]:
    return InfraDr().diagnose()
