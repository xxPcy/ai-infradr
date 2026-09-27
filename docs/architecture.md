# Architecture

AI InfraDr separates environment observation from diagnosis.

```text
System / Python / GPU / CUDA / Torch / NCCL
                  │
                  ▼
              Probes
                  │
                  ▼
       EnvironmentSnapshot v1
                  │
          ┌───────┴────────┐
          ▼                ▼
  JSON rule catalog   Procedural checks
          │                │
          └───────┬────────┘
                  ▼
               Issues
                  │
          ┌───────┴────────┐
          ▼                ▼
       Console            JSON
```

## Probe contract

A probe gathers structured facts only. It should not decide whether the facts represent a problem.

```python
class Probe:
    name: str

    def available(self) -> bool:
        ...

    def collect(self) -> ProbeResult:
        ...
```

Missing commands or optional libraries should produce an unavailable/skipped state where possible, not terminate the whole scan.

## Snapshot contract

All environment sources are normalized into `EnvironmentSnapshot`. The schema has an explicit version so future adapters (Conda, Dockerfile, requirements, remote snapshots) can feed the same diagnosis layer.

## Rule catalog

Simple compatibility constraints live in `src/ai_infradr/rules/catalog.v1.json`. Each finding has a stable code, severity, explanation, evidence fields, and safe suggestions.

Checks requiring dynamic interpretation can remain procedural until the rule schema can express them cleanly. This avoids making the declarative rule language overly complex too early.

## AI boundary

The v0.1 core contains no LLM dependency. A future AI explanation layer may summarize or prioritize deterministic findings, but it should not be the sole source of compatibility claims.
