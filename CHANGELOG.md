# Changelog

All notable changes to AI InfraDr will be documented here.

## [Unreleased]

### Planned

- Real NVIDIA GPU environment validation
- FlashAttention / Triton / Transformers probes and rules

## [0.1.0] - 2026-09-27

### Added

- System, Python, NVIDIA GPU, CUDA Toolkit, PyTorch, and NCCL probes
- Versioned `EnvironmentSnapshot` schema
- Versioned JSON compatibility rule catalog
- Evidence-backed deterministic diagnosis engine
- Rich console report and machine-readable JSON output
- CI-oriented `--fail-on high|medium`
- Graceful degradation when optional tooling is missing
- Unit test suite and GitHub Actions CI
