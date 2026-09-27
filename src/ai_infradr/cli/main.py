from __future__ import annotations

import argparse
import json
import sys

from ai_infradr import __version__
from ai_infradr.app import InfraDr
from ai_infradr.reports import build_json_report, render_console_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-infradr",
        description="Diagnose PyTorch/CUDA/NVIDIA/NCCL environment problems.",
    )
    parser.add_argument("--version", action="version", version=f"ai-infradr {__version__}")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable JSON report.")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show additional diagnostic details.",
    )
    parser.add_argument(
        "--fail-on",
        choices=["never", "high", "medium"],
        default="never",
        help="Return exit code 1 when issues at or above the chosen severity are found.",
    )
    return parser


def _should_fail(issues, fail_on: str) -> bool:
    if fail_on == "never":
        return False
    levels = {"critical": 3, "high": 2, "medium": 1, "low": 0, "info": 0}
    threshold = 2 if fail_on == "high" else 1
    return any(levels[issue.severity.value] >= threshold for issue in issues)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    snapshot, issues = InfraDr().diagnose()

    if args.json:
        print(json.dumps(build_json_report(snapshot, issues), indent=2, ensure_ascii=False))
    else:
        render_console_report(snapshot, issues, verbose=args.verbose)

    return 1 if _should_fail(issues, args.fail_on) else 0


if __name__ == "__main__":
    sys.exit(main())
