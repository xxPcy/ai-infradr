from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ai_infradr.models.issue import Issue, Severity
from ai_infradr.models.snapshot import EnvironmentSnapshot

_SEVERITY_STYLE = {
    Severity.CRITICAL: "bold red",
    Severity.HIGH: "red",
    Severity.MEDIUM: "yellow",
    Severity.LOW: "cyan",
    Severity.INFO: "dim",
}


def _value(value: object, fallback: str = "unavailable") -> str:
    if value is None or value == "":
        return fallback
    return str(value)


def render_console_report(
    snapshot: EnvironmentSnapshot,
    issues: list[Issue],
    *,
    verbose: bool = False,
    console: Console | None = None,
) -> None:
    console = console or Console()
    console.print(
        Panel.fit(
            "[bold]AI InfraDr[/bold]\nEvidence-based AI environment diagnostics",
            border_style="blue",
        )
    )

    table = Table(show_header=True, header_style="bold")
    table.add_column("Area")
    table.add_column("Detected")
    table.add_column("Status")

    system = snapshot.system
    table.add_row(
        "System",
        f"{_value(system.get('os'))} {_value(system.get('release'), '')}".strip(),
        "✓",
    )
    table.add_row("Python", _value(snapshot.python.get("version")), "✓")

    gpu = snapshot.gpu
    if gpu.get("available"):
        names = sorted({str(d.get("name")) for d in gpu.get("devices", []) if d.get("name")})
        name_text = ", ".join(names) if names else "NVIDIA GPU"
        table.add_row("GPU", f"{gpu.get('device_count', 0)} × {name_text}", "✓")
        table.add_row("Driver", _value(gpu.get("driver_version")), "✓")
        table.add_row("Driver CUDA", _value(gpu.get("driver_cuda_supported")), "✓")
    else:
        table.add_row("GPU", "NVIDIA GPU not detected", "-")

    torch = snapshot.torch
    if torch.get("installed"):
        torch_status = "✓" if not snapshot.probe_errors.get("torch") else "!"
        table.add_row("PyTorch", _value(torch.get("version")), torch_status)
        table.add_row(
            "Torch CUDA",
            _value(torch.get("cuda_runtime"), "CPU-only"),
            "✓" if torch.get("cuda_available") else "-",
        )
    else:
        table.add_row("PyTorch", "not installed", "-")

    cuda = snapshot.cuda
    table.add_row(
        "CUDA toolkit",
        _value(cuda.get("toolkit_version"), "nvcc not found"),
        "✓" if cuda.get("toolkit_version") else "-",
    )

    nccl = snapshot.nccl
    table.add_row(
        "NCCL",
        _value(nccl.get("version"), "unavailable"),
        "✓" if nccl.get("available") else "-",
    )
    console.print(table)

    if not issues:
        console.print("\n[bold green]No known v0.1 compatibility issues detected.[/bold green]")
        return

    console.print("\n[bold]Detected issues[/bold]")
    for issue in issues:
        style = _SEVERITY_STYLE[issue.severity]
        heading = Text(f"{issue.severity.value.upper()}  {issue.code}", style=style)
        console.print(heading)
        console.print(f"[bold]{issue.title}[/bold]")
        console.print(issue.summary)
        if issue.evidence:
            console.print("  Evidence:")
            for evidence in issue.evidence:
                console.print(f"   • {evidence}")
        if issue.suggestions:
            console.print("  Suggested next step:")
            for suggestion in issue.suggestions:
                console.print(f"   • {suggestion}")
        if verbose and issue.references:
            console.print("  References:")
            for reference in issue.references:
                console.print(f"   • {reference}")
        console.print()
