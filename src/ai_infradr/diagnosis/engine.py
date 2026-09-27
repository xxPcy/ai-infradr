from __future__ import annotations

from ai_infradr.models.issue import Issue, Severity
from ai_infradr.models.snapshot import EnvironmentSnapshot

from .rule_engine import evaluate_catalog


class DiagnosisEngine:
    """Deterministic, evidence-based diagnostics for an environment snapshot."""

    def diagnose(self, snapshot: EnvironmentSnapshot) -> list[Issue]:
        issues: list[Issue] = []
        issues.extend(self._probe_errors(snapshot))
        issues.extend(self._platform_support(snapshot))
        issues.extend(evaluate_catalog(snapshot))
        issues.extend(self._gpu_visibility(snapshot))

        rank = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }
        return sorted(issues, key=lambda item: (rank[item.severity], item.code))

    @staticmethod
    def _probe_errors(snapshot: EnvironmentSnapshot) -> list[Issue]:
        issues = []
        for probe, error in sorted(snapshot.probe_errors.items()):
            issues.append(
                Issue(
                    code=f"PROBE_{probe.upper()}_FAILED",
                    severity=Severity.MEDIUM,
                    title=f"{probe} probe could not complete",
                    summary=(
                        "Some diagnostic evidence is unavailable, "
                        "so later checks may be incomplete."
                    ),
                    evidence=[error],
                    suggestions=[
                        "Re-run with --verbose and verify the affected command/module manually."
                    ],
                    metadata={"source": "probe-boundary"},
                )
            )
        return issues

    @staticmethod
    def _platform_support(snapshot: EnvironmentSnapshot) -> list[Issue]:
        os_name = snapshot.system.get("os")
        if os_name and os_name != "Linux":
            return [
                Issue(
                    code="PLATFORM_NOT_PRIMARY_TARGET",
                    severity=Severity.INFO,
                    title=f"{os_name} is not the primary v0.1 target",
                    summary="AI InfraDr v0.1 focuses on Linux + NVIDIA environments.",
                    evidence=[f"Detected operating system: {os_name}"],
                    suggestions=[
                        "Use the JSON snapshot for inspection; "
                        "Linux-specific checks may be skipped."
                    ],
                    metadata={"source": "engine"},
                )
            ]
        return []

    @staticmethod
    def _gpu_visibility(snapshot: EnvironmentSnapshot) -> list[Issue]:
        physical = int(snapshot.gpu.get("device_count") or 0)
        torch_count = int(snapshot.torch.get("device_count") or 0)
        visible = snapshot.cuda.get("visible_devices")
        if physical and snapshot.torch.get("cuda_available") and physical != torch_count:
            severity = Severity.INFO if visible is not None else Severity.MEDIUM
            evidence = [
                f"nvidia-smi GPU count: {physical}",
                f"PyTorch visible GPU count: {torch_count}",
            ]
            if visible is not None:
                evidence.append(f"CUDA_VISIBLE_DEVICES={visible!r}")
            return [
                Issue(
                    code="GPU_VISIBILITY_DIFFERS",
                    severity=severity,
                    title="PyTorch sees a different number of GPUs than nvidia-smi",
                    summary=(
                        "GPU masking, container configuration, or permissions can change "
                        "device visibility."
                    ),
                    evidence=evidence,
                    suggestions=[
                        "Verify CUDA_VISIBLE_DEVICES and container/runtime GPU allocation."
                    ],
                    metadata={"source": "engine"},
                )
            ]
        return []
