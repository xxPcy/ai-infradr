# Contributing

AI InfraDr is intentionally split into probes, normalized snapshots, and deterministic diagnostics.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
ruff check src tests
pytest
```

## Adding a probe

1. Implement `Probe` in `src/ai_infradr/probes/`.
2. Return structured facts only. Do not embed diagnosis or remediation logic in probes.
3. Make missing tools/modules degrade gracefully instead of crashing the scan.
4. Add unit tests that do not require a physical GPU whenever possible.

## Adding a diagnostic

Every diagnostic should include:

- a stable error code;
- severity;
- evidence from the snapshot;
- a cautious explanation;
- a safe next step.

Avoid declaring two versions incompatible unless there is evidence for an actual compatibility constraint.
