# 🩺 AI InfraDr

**Diagnose broken PyTorch, CUDA, NVIDIA GPU, and NCCL environments with evidence instead of guesswork.**

```bash
pip install ai-infradr
ai-infradr
```

Example output:

```text
AI InfraDr

Area          Detected                         Status
System        Linux 6.8                       ✓
GPU           8 × NVIDIA A800                 ✓
Driver        570.86                          ✓
Driver CUDA   12.8                            ✓
PyTorch       2.7.1+cu126                     ✓
Torch CUDA    12.6                            ✓
NCCL          2.26.2                          ✓

Detected issues
LOW  CUDA_TOOLKIT_DIFFERS_FROM_TORCH_RUNTIME
System CUDA toolkit differs from PyTorch CUDA runtime
Evidence:
 • nvcc toolkit: 12.8
 • torch CUDA runtime: 12.6
```

AI InfraDr is not a version printer. It normalizes environment facts, applies deterministic compatibility checks, shows the evidence behind each finding, and gives cautious next steps.

## Why

AI environments fail in ways that are hard to diagnose:

- PyTorch installs successfully but `torch.cuda.is_available()` is false.
- `nvidia-smi`, `nvcc`, and `torch.version.cuda` show different CUDA versions.
- A CPU-only PyTorch wheel is installed on a GPU machine.
- The host driver is too old for the CUDA runtime used by PyTorch.
- A container sees fewer GPUs than the host.
- NCCL is unavailable in a multi-GPU environment.

The project treats these as compatibility/debugging problems, not as a request to blindly reinstall everything.

## v0.1 checks

- Linux/system information
- Python interpreter and environment
- NVIDIA GPUs and driver via `nvidia-smi`
- Driver-reported maximum CUDA support
- CUDA Toolkit / `nvcc`
- PyTorch version, bundled CUDA runtime, CUDA availability, visible devices
- cuDNN version when available
- NCCL version exposed by PyTorch
- GPU visibility mismatches
- Driver ↔ PyTorch CUDA runtime compatibility
- System CUDA Toolkit ↔ PyTorch CUDA runtime differences
- Graceful degradation when optional tools are missing

## Usage

### Human-readable report

```bash
ai-infradr
```

### JSON for automation

```bash
ai-infradr --json
```

### Fail CI on serious findings

```bash
ai-infradr --fail-on high
```

or:

```bash
ai-infradr --fail-on medium
```

### More detail

```bash
ai-infradr --verbose
```

You can also run it as a Python module:

```bash
python -m ai_infradr
```

## Important CUDA distinction

AI InfraDr keeps these concepts separate:

1. **NVIDIA driver CUDA support** — reported by `nvidia-smi`.
2. **System CUDA Toolkit** — usually reported by `nvcc --version`.
3. **PyTorch CUDA runtime** — reported by `torch.version.cuda`.

Different Toolkit and PyTorch runtime versions are not automatically a bug. PyTorch wheels commonly ship with their own CUDA runtime. The difference becomes more relevant when compiling/loading CUDA extensions.

## Architecture

```text
Probes
  ↓
Structured EnvironmentSnapshot
  ↓
Deterministic Diagnosis Engine
  ↓
Evidence-backed Issues
  ↓
Console / JSON reports
```

The core does not require an LLM or API key. Future AI explanations should remain an optional layer above deterministic evidence.

## Python API

```python
from ai_infradr import InfraDr

snapshot, issues = InfraDr().diagnose()

for issue in issues:
    print(issue.code, issue.severity.value)
```

## Development

```bash
git clone https://github.com/xxPcy/ai-infradr.git
cd ai-infradr

python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

ruff check src tests
pytest
```

## Roadmap

- **v0.1** — Linux + NVIDIA + Python + PyTorch + CUDA + NCCL
- **v0.2** — FlashAttention + Transformers + Triton
- **v0.3** — vLLM + SGLang + DeepSpeed
- **v0.4** — Docker / Conda / uv environment adapters and offline scans
- **v0.5** — GitHub Action compatibility checks
- **v1.0** — optional AI explanation, safe fix planning, community compatibility rules

## Design principles

- Evidence before recommendations.
- Stable diagnostic error codes.
- Missing optional dependencies must not crash the scan.
- Never silently modify the user's environment.
- Do not treat every version difference as incompatibility.
- Core diagnostics work offline and without an API key.

## Contributing

Contributions are welcome, especially reproducible compatibility cases and additional probes. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
