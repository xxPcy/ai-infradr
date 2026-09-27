# AI InfraDr — Codex Handoff & Test Guide

## 1. Handoff goal

This repository is the `v0.1.0` MVP of **AI InfraDr**, a local, evidence-based diagnostic CLI for AI infrastructure environments.

The current release focuses on:

- Linux/system facts
- Python runtime/environment
- NVIDIA GPU discovery through `nvidia-smi`
- NVIDIA driver and driver-reported CUDA support
- CUDA Toolkit / `nvcc`
- PyTorch and its bundled CUDA runtime
- CUDA availability and visible GPU count through PyTorch
- cuDNN/NCCL information exposed by PyTorch
- deterministic compatibility findings
- human-readable and JSON reports

The core must remain useful **without an LLM, API key, database, web service, or automatic system modification**.

## 2. Naming contract — do not change

The project has been deliberately renamed. Treat the following names as canonical:

| Surface | Canonical name |
|---|---|
| Product/display name | `AI InfraDr` |
| GitHub repository | `ai-infradr` |
| Python distribution / PyPI name | `ai-infradr` |
| CLI command | `ai-infradr` |
| Python package/import | `ai_infradr` |
| Main Python API class | `InfraDr` |

Expected examples:

```bash
ai-infradr --version
python -m ai_infradr --version
```

```python
from ai_infradr import InfraDr

snapshot, issues = InfraDr().diagnose()
```

The wheel filename is expected to use Python's normalized underscore form, for example:

```text
ai_infradr-0.1.0-py3-none-any.whl
```

That is normal and should **not** be changed back to the hyphenated CLI/distribution spelling.

## 3. Current implementation status

At handoff time the following checks have already passed in the build environment:

```text
pytest:                         14/14 passed
python -m ai_infradr --version: ai-infradr 0.1.0
installed CLI --version:        ai-infradr 0.1.0
JSON report parsing:            passed
wheel build:                    passed
rule catalog included in wheel: passed
legacy package paths:          none found in wheel
```

The build environment did **not** expose an NVIDIA GPU, so real NVIDIA/CUDA/NCCL behavior still needs hardware validation.

## 4. Architecture to preserve

Keep the diagnostic path deterministic:

```text
Probes
  ↓
Structured EnvironmentSnapshot
  ↓
Rule / Diagnosis Engine
  ↓
Evidence-backed Issues
  ↓
Console / JSON reports
```

Important design rules:

1. Probes observe facts; they should not make broad compatibility claims.
2. Diagnosis consumes normalized facts and emits stable issue codes.
3. Every actionable finding should include evidence.
4. Missing optional tools must degrade gracefully instead of crashing.
5. A difference between system CUDA Toolkit and PyTorch CUDA runtime is not automatically an error.
6. Never automatically run `sudo`, uninstall packages, replace drivers, or mutate the user's environment.
7. AI-generated explanation can be added later, but deterministic evidence remains the source of truth.

## 5. Repository map

```text
ai-infradr/
├── src/ai_infradr/
│   ├── app.py                 # InfraDr orchestration
│   ├── cli/                   # CLI entry point
│   ├── probes/                # system/python/GPU/CUDA/torch/NCCL probes
│   ├── models/                # normalized snapshot + issue models
│   ├── diagnosis/             # deterministic diagnosis/rule engine
│   ├── rules/                 # versioned JSON compatibility rules
│   └── reports/               # console + JSON reporting
├── tests/
├── examples/
├── docs/
├── .github/
├── pyproject.toml
├── README.md
└── CODEX_HANDOFF.md
```

## 6. Codex setup

Use Python 3.10+.

Recommended clean environment:

```bash
git clone https://github.com/xxPcy/ai-infradr.git
cd ai-infradr

python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e '.[dev]'
```

If the repository has not been uploaded yet, start directly from the unpacked project directory instead of cloning.

## 7. Required baseline tests

Run all of these before editing code:

```bash
pytest -q
ruff check src tests
ai-infradr --version
python -m ai_infradr --version
ai-infradr --json > /tmp/ai-infradr.json
python -m json.tool /tmp/ai-infradr.json > /dev/null
```

Expected version:

```text
ai-infradr 0.1.0
```

Also verify imports:

```bash
python - <<'PY'
from ai_infradr import InfraDr, EnvironmentSnapshot, run_diagnosis
print(InfraDr, EnvironmentSnapshot, run_diagnosis)
PY
```

## 8. Naming regression test

There must be no stale code/package references to the previous project/API naming.

Run:

```bash
python - <<'PY'
from pathlib import Path

legacy = [
    "AI Infra " + "Doc" + "tor",
    "AI " + "Doc" + "tor",
    "ai-" + "doc" + "tor",
    "ai_" + "doc" + "tor",
    "ai-infra-" + "doc" + "tor",
    "ai_infra_" + "doc" + "tor",
]

hits = []
for path in Path(".").rglob("*"):
    if not path.is_file() or any(part in {".git", ".venv"} for part in path.parts):
        continue
    if path.suffix in {".whl", ".pyc"}:
        continue
    try:
        text = path.read_text()
    except (UnicodeDecodeError, OSError):
        continue
    for token in legacy:
        if token in text:
            hits.append((str(path), token))

print(hits)
raise SystemExit(1 if hits else 0)
PY
```

Expected result: `[]` and exit code 0.

## 9. Package/build validation

Build the package:

```bash
rm -rf dist build src/*.egg-info
python -m build
python -m twine check dist/*
```

Expected artifacts should include an sdist and a wheel similar to:

```text
dist/ai_infradr-0.1.0-py3-none-any.whl
```

Then verify installation from the wheel in a clean environment:

```bash
python -m venv /tmp/ai-infradr-wheel-test
source /tmp/ai-infradr-wheel-test/bin/activate
pip install dist/ai_infradr-0.1.0-py3-none-any.whl
ai-infradr --version
ai-infradr --json
```

Check that `src/ai_infradr/rules/catalog.v1.json` is included in the installed wheel and that rule loading works outside the source checkout.

## 10. NVIDIA GPU validation — highest priority

Run the following on at least one real NVIDIA Linux environment with PyTorch installed:

```bash
nvidia-smi
which nvcc || true
nvcc --version || true

python - <<'PY'
import torch
print('torch:', torch.__version__)
print('torch.version.cuda:', torch.version.cuda)
print('cuda_available:', torch.cuda.is_available())
print('device_count:', torch.cuda.device_count())
print('cudnn:', torch.backends.cudnn.version())
try:
    print('nccl:', torch.cuda.nccl.version())
except Exception as exc:
    print('nccl unavailable:', repr(exc))
PY

ai-infradr
ai-infradr --verbose
ai-infradr --json
```

Compare the raw commands with the values reported by AI InfraDr.

Validate specifically that:

- GPU model names and counts match `nvidia-smi`.
- NVIDIA driver version is parsed correctly.
- driver-reported CUDA support is not confused with installed CUDA Toolkit.
- `nvcc` Toolkit version is parsed correctly when present.
- PyTorch version and `torch.version.cuda` are exact.
- `torch.cuda.is_available()` and device count are exact.
- cuDNN/NCCL absence never crashes the scan.
- a different Toolkit version vs PyTorch runtime produces cautious wording, not a false hard incompatibility.

## 11. Environment scenarios to exercise

Test as many of these as available:

### A. CPU-only machine

Expected: no crash; GPU/CUDA/NCCL fields degrade gracefully.

### B. NVIDIA GPU + CPU-only PyTorch wheel

Expected: AI InfraDr should surface the relevant mismatch with evidence instead of recommending arbitrary driver reinstallations.

### C. NVIDIA GPU + CUDA-enabled PyTorch

Expected: hardware/runtime details match PyTorch and `nvidia-smi`.

### D. `nvidia-smi` available but no `nvcc`

Expected: driver/GPU data still works; CUDA Toolkit is reported unavailable, not treated as a fatal error.

### E. `nvcc` Toolkit version differs from `torch.version.cuda`

Expected: distinguish Toolkit vs PyTorch runtime and avoid claiming they must be identical.

### F. Multiple GPUs

Expected: device counts and visible devices are internally consistent; mismatches should carry concrete evidence.

### G. Containerized environment

If available, verify host driver exposure and container-visible GPUs without assuming the container includes a full CUDA Toolkit.

## 12. CLI behavior to verify

Commands:

```bash
ai-infradr
ai-infradr --verbose
ai-infradr --json
ai-infradr --fail-on high
ai-infradr --fail-on medium
```

Requirements:

- default output is concise and readable;
- JSON contains the normalized snapshot, issues, and summary;
- JSON output contains no Rich formatting/control sequences;
- `--fail-on high` returns non-zero only when high-or-higher findings exist;
- `--fail-on medium` returns non-zero for medium-or-higher findings;
- normal scanning defaults to exit code 0;
- unexpected missing system commands do not generate Python tracebacks for ordinary users.

## 13. What Codex may fix during validation

Codex may fix bugs discovered by reproducible tests, especially:

- incorrect parsing of `nvidia-smi` / `nvcc` output;
- distro/kernel/platform edge cases;
- unexpected PyTorch API exceptions;
- package-resource loading failures after wheel installation;
- false-positive compatibility findings;
- CLI exit-code bugs;
- JSON serialization bugs;
- stale naming references;
- test coverage for reproduced failures.

For every bug fix:

1. first capture a reproducible case or fixture;
2. add/update a regression test;
3. implement the smallest robust fix;
4. rerun the full suite;
5. report files changed and why.

## 14. Out of scope for v0.1 validation

Do not expand the release just because the architecture makes it possible. These are roadmap items, not required for this validation pass:

- FlashAttention
- Transformers
- Triton
- vLLM
- SGLang
- DeepSpeed
- Dockerfile/requirements offline scanning
- GitHub Action compatibility gate
- LLM-generated explanations
- automatic package fixing

A small, accurate v0.1 is preferred over a broad release with false positives.

## 15. Acceptance criteria for hand-back

Codex should return the project only after:

- [ ] all unit tests pass;
- [ ] Ruff passes;
- [ ] editable installation works;
- [ ] wheel and sdist build successfully;
- [ ] Twine check passes;
- [ ] wheel installation works in a clean venv;
- [ ] `ai-infradr` command works after installation;
- [ ] `python -m ai_infradr` works;
- [ ] JSON output parses cleanly;
- [ ] package rule catalog loads from the installed wheel;
- [ ] no stale old project names remain;
- [ ] at least one real NVIDIA environment has been manually cross-checked;
- [ ] any discovered bug has a regression test;
- [ ] no automatic destructive fix behavior was introduced.

## 16. Copy/paste prompt for Codex

Use this prompt when handing the repository to Codex:

> You are validating `AI InfraDr v0.1.0` for a public GitHub/PyPI release. Read `CODEX_HANDOFF.md`, `README.md`, `docs/architecture.md`, and `pyproject.toml` first. Do not rename the project: display name is `AI InfraDr`, repository/distribution/CLI is `ai-infradr`, import package is `ai_infradr`, and the main API class is `InfraDr`. Run the baseline tests before changing anything. Then validate installation, package building, CLI/JSON behavior, rule-resource packaging, naming consistency, and—if this machine has NVIDIA hardware—cross-check every reported NVIDIA/CUDA/PyTorch/NCCL fact against `nvidia-smi`, `nvcc`, and PyTorch directly. Fix only reproducible bugs; add a regression test for each fix. Do not add v0.2 features and do not introduce automatic environment modification. At the end, give me: (1) commands run, (2) test/build results, (3) GPU environment facts if available, (4) bugs found, (5) files changed, (6) remaining release blockers, and (7) whether you recommend publishing v0.1.0.

## 17. Next development milestone after validation

Only after v0.1 is stable on real NVIDIA environments, proceed to v0.2:

```text
FlashAttention
Transformers
Triton
```

Keep the same pattern: independent probes → normalized facts → data/rule-driven deterministic diagnosis → evidence-backed output.
