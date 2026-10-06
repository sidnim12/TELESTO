# BioControlOS

An uncertainty-aware, process-agnostic research platform for autonomous biological manufacturing.

> **Status: Phase 0 — architecture and interfaces.** No biological process has been selected. The repository contains no validated biological models, sensor ranges, process constants, or production-control logic.

## Core principle

The autonomy engine interacts with a process only through `ProcessAdapter`. Process-specific biology, sensors, actuators, quality attributes, constraints, and rewards belong in replaceable adapters.

`BIOLOGICAL_PROCESS_DECISION_REQUIRED` marks every decision that depends on the future target process.

## Repository map

- `apps/` — API and dashboard application boundaries
- `biocontrolos/core/` — process-independent state, uncertainty, rewards, constraints, and memory contracts
- `biocontrolos/process/` — process adapter boundary; `synthetic/` is reserved for an abstract test process
- `biocontrolos/digital_twin/` — twin contracts and future implementations
- `biocontrolos/control/`, `biocontrolos/rl/` — classical and learning-based control research
- `biocontrolos/agents/`, `biocontrolos/llm/` — supervisory reasoning only, never direct actuator control
- `biocontrolos/safety/` — independent validation, risk, and human-approval gates
- `biocontrolos/memory/` — cross-batch trajectory and experiment history
- `experiments/` — baselines, benchmarks, and ablations
- `docs/` — architecture, assumptions, and phased plan

## Development guardrails

1. Never select or infer a biological target without an explicit decision.
2. No LLM, learned policy, or optimizer may bypass `SafetyGate`.
3. New process behavior must be introduced through a `ProcessAdapter`.
4. Synthetic results validate software behavior only; they do not demonstrate biological validity.

## Getting started

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
```

See [docs/architecture.md](docs/architecture.md), [docs/assumptions.md](docs/assumptions.md), and [docs/roadmap.md](docs/roadmap.md).
