# Phased implementation plan

| Phase | Scope | Exit criterion |
| --- | --- | --- |
| 0 | Architecture, contracts, documentation | Core interfaces compile and boundary tests pass |
| 1 | Fermentation digital twin | IndPenSim / PenSimPy runs behind a TELESTO `ProcessAdapter`; complete seeded batches, trajectories, constraints, and interface tests are reproducible |
| 2 | Control baselines | Recipe, PID, and MPC baselines run under one evaluation protocol |
| 3 | Scale and operating-regime shifts | Reproducible virtual shifts expose performance degradation without claiming physical scale-up validation |
| 4 | State, uncertainty, and regime detection | Calibration, detection, and missing/noisy-observation behavior are evaluated |
| 5 | Adaptive decision policy | Policy adaptation is compared with frozen and classical baselines under held-out shifts |
| 6 | Information as an action | Control, measure, experiment, wait, and escalate choices are compared under explicit information budgets |
| 7 | Counterfactual evaluation | Digital-twin rollouts rank candidate decisions with uncertainty, cost, and risk |
| 8 | Experience memory | Cross-batch retrieval measurably changes and improves later decisions |
| 9 | Process knowledge and LLM interface | Unstructured records become typed, traceable knowledge; the LLM has no actuator authority |
| 10 | Full TELESTO integration | The end-to-end loop operates through constraints, safety, and human approval boundaries |
| 11 | Ablation and robustness studies | Multiple seeds, held-out regimes, faults, noise, missing data, and component ablations quantify contribution |

Any move from the IndPenSim / PenSimPy testbed to laboratory or plant control
requires a separate evidence-backed decision, domain adapter, safety analysis,
and validation plan.
