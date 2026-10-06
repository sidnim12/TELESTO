# Architecture

## Process-independent autonomy loop

```text
observe → estimate state → quantify uncertainty → decide whether information is sufficient
  ├─ insufficient: measure / experiment / simulate / wait / escalate
  └─ sufficient: propose strategy → twin rollout → constraint validation → safety gate
                                                          ├─ execute
                                                          ├─ modify or reject
                                                          └─ require human approval
                                                               ↓
                                                      remember outcome
```

The only process boundary is `biocontrolos.process.base.ProcessAdapter`. Core services must not import a real-process adapter.

## Responsibilities

| Component | Responsibility | Must not do |
| --- | --- | --- |
| State estimator | Infer a belief state from observations and history | Assume full observability |
| Uncertainty estimator | Express confidence, missing information, and calibration | Conceal uncertainty as certainty |
| Digital twin | Predict candidate trajectories | Authorize actions |
| Decision engine | Compare control, information, experiment, simulation, wait, and escalation choices | Bypass safety |
| LLM layer | Convert unstructured context to typed hypotheses/constraints | Set raw actuator values |
| Safety gate | Independently validate, modify, reject, or escalate actions | Depend on an LLM decision |
| Memory | Retain batch outcomes and overrides | Replace validated source data |

## Package dependency direction

```text
apps / experiments
        ↓
agents, control, rl, llm
        ↓
digital_twin, core, safety, memory
        ↓
process.base
        ↓
process.synthetic (development only)
```
