# Phased implementation plan

| Phase | Scope | Exit criterion |
| --- | --- | --- |
| 0 | Architecture, contracts, documentation | Core interfaces compile and boundary tests pass |
| 1 | Synthetic simulator and PID/MPC baselines | Reproducible seeded benchmark scenarios |
| 2 | Standard RL baselines | Comparable PPO/SAC experiment protocol |
| 3 | State and uncertainty estimation | Calibration evaluated under noise and missingness |
| 4 | Active information acquisition | Measurement-cost trade-offs benchmarked |
| 5 | Twin-based planning | Candidate rollouts evaluated against baselines |
| 6 | Safety-constrained decisions | Violation and escalation behavior tested |
| 7 | Cross-batch memory | Improvement evaluated across batches |
| 8 | LLM supervision | Typed, auditable context extraction only |
| 9 | Human approval workflow | Approval and override audit trail |
| 10 | Benchmarks and ablations | Multiple seeds, OOD tests, and ablations |
| 11+ | Real process adapter | Only after `BIOLOGICAL_PROCESS_DECISION_REQUIRED` is resolved |
