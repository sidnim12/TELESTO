# TELESTO

### Scale-Adaptive Intelligence for Biological Manufacturing

> **Learning how biological processes change, deciding what to do next, and knowing when more information is needed.**

[![Status: Research](https://img.shields.io/badge/status-research-blue)](#project-status)
[![Domain: Biomanufacturing](https://img.shields.io/badge/domain-biomanufacturing-purple)](#overview)
[![RL: Decision Intelligence](https://img.shields.io/badge/RL-sequential%20decision--making-orange)](#reinforcement-learning)
[![LLM: Supervisory](https://img.shields.io/badge/LLM-supervisory%20reasoning-green)](#large-language-models)
[![Digital Twin](https://img.shields.io/badge/digital%20twin-hybrid%20modeling-red)](#digital-twin)

> **Current focus:** research and architecture definition. No biological process has been frozen yet.

---

## Table of Contents

- [Overview](#overview)
- [The Problem](#the-problem)
- [Core Research Question](#core-research-question)
- [What TELESTO Is](#what-telesto-is)
- [Why This Is Different](#why-this-is-different)
- [System Architecture](#system-architecture)
- [Decision Loop](#decision-loop)
- [Reinforcement Learning](#reinforcement-learning)
- [Large Language Models](#large-language-models)
- [Digital Twin](#digital-twin)
- [Active Information Acquisition](#active-information-acquisition)
- [Safety and Human Oversight](#safety-and-human-oversight)
- [Experience and Memory](#experience-and-memory)
- [Research Methodology](#research-methodology)
- [Evaluation](#evaluation)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Three-Month Research Plan](#three-month-research-plan)
- [Project Status](#project-status)
- [Research Principles](#research-principles)
- [Limitations and Non-Goals](#limitations-and-non-goals)
- [Reproducibility](#reproducibility)
- [License](#license)

---

# Overview

**TELESTO** is a research platform for **scale-adaptive, uncertainty-aware decision intelligence in biological manufacturing**.

Biological manufacturing processes are nonlinear, partially observable, and sensitive to changes in scale, equipment, operating conditions, and biological state.

A process that performs well at laboratory scale may behave differently at pilot or production scale. Engineers may then need to rely on additional experiments, troubleshooting, expert judgment, and controller retuning to determine how the process should be adapted.

TELESTO investigates whether an intelligent system can:

1. infer the current process state,
2. predict how the process may evolve,
3. recognize when previously learned behavior no longer transfers,
4. decide whether to intervene, measure, experiment, wait, or escalate,
5. safely adapt decisions under changing regimes,
6. learn from outcomes and previous process experience.

The platform combines:

**mechanistic modeling + digital twins + reinforcement learning + active learning/experimental design + LLM-based process knowledge + optimization + safety constraints + human oversight.**

---

# The Problem

## The laboratory-to-production gap

A biological process may work well at one scale and behave differently after scale-up.

A simplified progression looks like:

```text
Laboratory
10 mL
   ↓
Pilot
1 L
   ↓
Scale-up
100 L
   ↓
Production
1,000+ L
```

The nominal recipe may remain similar while the physical and biological dynamics change.

Examples include:

- mixing and concentration gradients,
- mass and heat transfer,
- residence-time effects,
- sensor behavior,
- actuator limitations,
- equipment changes,
- biological adaptation,
- process disturbances.

This creates a costly loop:

```text
Process change
     ↓
Run experiment
     ↓
Measure outcome
     ↓
Investigate
     ↓
Modify process
     ↓
Run again
     ↓
Repeat
```

### TELESTO's problem statement

> **Can we safely transfer and adapt process-control knowledge across biological manufacturing scales and operating regimes without repeatedly rediscovering the process through trial-and-error?**

The exact initial biological process will be selected through the research phase rather than assumed in advance.

---

# Core Research Question

> **Can an uncertainty-aware agent transfer and adapt biological-process decision policies under scale and operating-regime shifts while deciding when additional measurements or experiments are worth their cost?**

This formulation intentionally goes beyond:

- single-scale process optimization,
- generic digital twins,
- generic RL control,
- or LLM-based process assistants.

The research contribution, if supported by experiments, is expected to center on **scale transfer, uncertainty, active information acquisition, and bounded autonomy**.

---

# What TELESTO Is

TELESTO is a **decision-intelligence research system**, not an unconstrained autonomous controller.

At each decision point, the agent can reason over actions such as:

```text
CONTROL
    ↓
Change the process

MEASURE
    ↓
Acquire additional information

EXPERIMENT
    ↓
Perform a bounded information-gathering intervention

WAIT
    ↓
Avoid unnecessary intervention

ESCALATE
    ↓
Request human review
```

The goal is to optimize both:

- **process performance**, and
- **the information available for future decisions**.

---

# Why This Is Different

TELESTO does **not** claim that RL, LLMs, or digital twins are individually new in bioprocessing.

The research focus is their disciplined combination around a narrower problem:

> **What should an intelligent system do when the process it learned from is no longer exactly the process it is currently operating?**

That requires reasoning about:

- distribution shift,
- latent process state,
- uncertainty,
- scale transfer,
- sequential consequences,
- experiment cost,
- domain knowledge,
- and safety.

---

# System Architecture

```text
                     ┌──────────────────────────────┐
                     │   BIOLOGICAL PROCESS         │
                     │ reactor / process / plant    │
                     └──────────────┬───────────────┘
                                    │
                     telemetry / PAT / batch data
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │      STATE ESTIMATION        │
                     │ observed + latent process    │
                     └──────────────┬───────────────┘
                                    │
        SOPs / notes / reports      │
                │                   │
                ▼                   │
        ┌───────────────┐           │
        │      LLM      │───────────┘
        │ process       │
        │ knowledge     │
        └───────┬───────┘
                │
                ▼
        ┌───────────────────────────┐
        │ BELIEF / WORLD STATE      │
        │ state + uncertainty +     │
        │ semantic constraints      │
        └─────────────┬─────────────┘
                      │
                      ▼
        ┌───────────────────────────┐
        │     HYBRID DIGITAL TWIN   │
        │ mechanistic + learned     │
        │ + uncertainty model       │
        └─────────────┬─────────────┘
                      │
                      ▼
        ┌───────────────────────────┐
        │  COUNTERFACTUAL ENGINE    │
        │ simulate candidate paths  │
        └─────────────┬─────────────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
       RL POLICY   ACTIVE/BO     MPC / SOLVER
          │           │           │
          └───────────┼───────────┘
                      │
                      ▼
        ┌───────────────────────────┐
        │ SAFETY / FEASIBILITY GATE │
        │ hard constraints + risk   │
        └─────────────┬─────────────┘
                      │
                      ▼
        ┌───────────────────────────┐
        │ DECISION                  │
        │ control / measure /       │
        │ experiment / wait / human │
        └─────────────┬─────────────┘
                      │
                      ▼
             PROCESS OUTCOME
                      │
                      ▼
        ┌───────────────────────────┐
        │ EXPERIENCE / MEMORY       │
        │ state → action → outcome  │
        │ → error → lesson          │
        └─────────────┬─────────────┘
                      │
                      └──────→ next decision
```

---

# Decision Loop

TELESTO follows a closed-loop cycle:

```text
OBSERVE
   ↓
ESTIMATE STATE
   ↓
ASSESS UNCERTAINTY
   ↓
INTERPRET PROCESS KNOWLEDGE
   ↓
PREDICT FUTURE TRAJECTORIES
   ↓
GENERATE CANDIDATE DECISIONS
   ↓
SIMULATE COUNTERFACTUALS
   ↓
CHECK CONSTRAINTS
   ↓
SELECT ACTION
   ↓
CONTROL / MEASURE / EXPERIMENT / WAIT / ESCALATE
   ↓
OBSERVE OUTCOME
   ↓
UPDATE MODEL + MEMORY
   ↓
LEARN
```

The objective is **better decisions under uncertainty**, not autonomy for its own sake.

---

# Reinforcement Learning

RL is responsible for **sequential decision-making**.

Instead of predicting a single output, the policy learns:

> **Which action should be taken now, given that the current action changes the future process state?**

A simplified formulation is:

$$
s_t = \text{latent process state}
$$

$$
o_t = \text{available observations}
$$

$$
a_t \in \{\text{control, measure, experiment, wait, escalate}\}
$$

$$
r_t = \text{quality} + \text{yield} - \text{cost} - \text{risk} - \text{resource usage} - \text{information cost}
$$

Candidate methods include:

- PPO
- SAC
- model-based RL
- offline RL
- constrained RL
- risk-sensitive/distributional RL
- hierarchical RL

The final algorithm will be selected by empirical evidence rather than assumed in advance.

---

# Large Language Models

The LLM is **not the low-level process controller**.

Its role is to interpret information that is difficult to represent directly as numerical state:

- SOPs,
- batch records,
- process-development reports,
- operator observations,
- maintenance notes,
- deviation reports,
- scientific literature,
- engineering recommendations,
- historical context.

The intended interface is a **structured knowledge representation**, not free-form text passed directly into a controller.

Example:

```json
{
  "regime": "post_feed_transition",
  "historical_issue": "oxygen_limitation",
  "equipment": "reactor_02",
  "constraint": "avoid_high_agitation",
  "evidence": ["batch_17", "process_note_4"],
  "confidence": 0.84
}
```

### Design principle

| Layer | Responsibility |
|---|---|
| **LLM** | Semantic knowledge, context, evidence extraction |
| **RL** | Sequential decision-making |
| **Digital Twin** | Process dynamics and counterfactuals |
| **Optimization / MPC** | Short-horizon feasibility and constraints |
| **Safety Gate** | Independent validation / bounded autonomy |
| **Human** | Authority for high-consequence decisions |

---

# Digital Twin

The digital twin is the computational representation of the process.

TELESTO aims to combine:

### Mechanistic models

Represent known process dynamics and physical/biological structure.

### Data-driven models

Learn relationships not adequately captured by the mechanistic model.

### Surrogate models

Enable fast counterfactual evaluation during decision-making.

### Uncertainty estimation

Estimate when the system is operating outside regions where its model or policy is reliable.

The twin should support questions such as:

- What happens if we change this process variable?
- What happens if the current regime persists?
- What changes when scale or equipment changes?
- Which action has the highest expected long-term utility?
- When is additional information worth acquiring?

---

# Active Information Acquisition

A central TELESTO idea is:

> **Information can itself be an action.**

If the system is uncertain, it may be better to acquire information before changing the process.

For example:

```text
Ambiguous observation
        ↓
Is additional information valuable?
        ↓
   ┌────┴────┐
   │         │
  YES       NO
   │         │
Measure/   Act or
Experiment Wait
```

Potential methods include:

- Bayesian optimization,
- contextual bandits,
- value-of-information methods,
- active learning,
- model-based RL.

The evaluation should measure whether intelligent information acquisition reduces:

- experiment count,
- adaptation time,
- process loss,
- unnecessary interventions.

---

# Safety and Human Oversight

Learned policies are **never intended to be the only protection layer**.

A candidate action passes through:

```text
Learned Policy
      ↓
Feasibility Checks
      ↓
Process Constraints
      ↓
Risk / Uncertainty Assessment
      ↓
Human Gate (when required)
      ↓
Execution
```

TELESTO's intended autonomy ladder is:

### Level 0 — Analysis
Historical and simulated analysis only.

### Level 1 — Recommendation
System suggests actions; a human decides.

### Level 2 — Human-Approved Control
System proposes bounded process changes requiring approval.

### Level 3 — Limited Autonomy
Selected low-risk decisions may execute within explicit boundaries.

### Level 4 — Bounded Operational Autonomy
Autonomy is permitted only within validated safety envelopes.

The three-month research prototype is expected to remain well below unrestricted autonomous production control.

---

# Experience and Memory

Each process episode can be represented as:

```text
Initial Context
      ↓
Observed State
      ↓
Decision
      ↓
Expected Outcome
      ↓
Actual Outcome
      ↓
Prediction Error
      ↓
Lesson
```

This supports retrieval of prior experience across:

- process regimes,
- batches,
- interventions,
- failures,
- scale transitions,
- model errors,
- operator decisions.

Memory is intended to improve future decision-making rather than simply store logs.

---

# Research Methodology

## 1. Prior-Art Mapping

Systematically map:

- bioprocess controllers,
- RL methods,
- digital twins,
- active experimentation,
- LLM/agent systems,
- commercial platforms,
- patents,
- open-source environments.

For each method, record:

**state → action → reward → environment → model → uncertainty → scale transfer → active information → human-in-loop → validation → limitation.**

The research gap must be explicit before the final process is frozen.

---

## 2. Biological Process Selection

Candidate domains may include:

- microbial fermentation,
- mRNA manufacturing,
- biologics,
- cell/gene therapy manufacturing,
- other high-value biological processes.

The first process will be selected using:

- research-gap strength,
- RL suitability,
- observability,
- simulator availability,
- data availability,
- scale-transfer characteristics,
- measurable outcomes,
- validation feasibility,
- commercial relevance.

---

## 3. Environment / Digital Twin

Construct a validated environment containing:

- process dynamics,
- measurement noise,
- disturbances,
- parameter variation,
- equipment variation,
- scale/regime changes,
- operational constraints,
- failure scenarios.

---

## 4. Baselines

Compare against strong, appropriate baselines, such as:

- PID,
- MPC / NMPC,
- rule-based control,
- Bayesian optimization,
- PPO,
- SAC,
- offline/model-based RL,
- domain-specific state-of-the-art methods.

---

## 5. TELESTO Core

Evaluate:

- latent-state estimation,
- uncertainty estimation,
- scale/regime adaptation,
- active measurement selection,
- sequential intervention,
- bounded human escalation,
- cross-batch learning.

---

## 6. LLM Layer

Integrate:

- process documents,
- SOPs,
- operator notes,
- deviation reports,
- engineering constraints,
- scientific literature.

Evaluate whether structured process knowledge improves policy performance, adaptation speed, robustness, or safety.

---

# Evaluation

TELESTO will not be judged by RL reward alone.

## Process Performance

- yield
- quality
- productivity
- cycle time
- resource use
- process deviations

## Decision Quality

- cumulative utility
- regret
- intervention quality
- long-horizon performance
- constraint violations

## Scale / Regime Transfer

- performance degradation after shift
- adaptation time
- data required for adaptation
- experiments required
- zero-shot transfer performance

## Uncertainty

- calibration
- out-of-distribution detection
- abstention quality
- confidence reliability

## Information Efficiency

- measurements saved
- experiments saved
- information gained per experiment
- cost of information

## Safety

- constraint violations
- unsafe-action rate
- fallback frequency
- human-escalation quality

## Robustness

Evaluate under:

- sensor noise,
- equipment changes,
- parameter shifts,
- process disturbances,
- unseen regimes,
- simultaneous shifts.

---

# Technology Stack

## Scientific Computing

- Python
- NumPy
- SciPy
- JAX
- PyTorch
- CasADi

## Reinforcement Learning

- Gymnasium
- custom PyTorch/JAX implementations
- Stable-Baselines3 for reproducible baselines
- Ray RLlib when distributed training is justified

## Optimization / Control

- CasADi
- CVXPY
- OR-Tools
- MPC / mathematical programming solvers as appropriate

## Digital Twin

- mechanistic ODE/DAE models
- data-driven surrogate models
- hybrid modeling
- C++ only where profiling demonstrates a computational need

## LLM / Agent Layer

- LangGraph
- Pydantic structured schemas
- retrieval-augmented generation
- vLLM or equivalent model serving where appropriate

## Data

- PostgreSQL
- Parquet
- DuckDB
- Redis / event infrastructure when required

## Backend

- FastAPI — scientific/inference services
- Django / Django REST Framework — application, identity, administration and audit

## Frontend

- React
- TypeScript
- Next.js where appropriate
- scientific visualization tooling

## Infrastructure

- Linux
- Docker
- GitHub Actions
- cloud deployment as required

---

# Repository Structure

```text
TELESTO/
│
├── research/
│   ├── literature/
│   ├── prior_art/
│   ├── experiments/
│   └── reports/
│
├── environments/
│   ├── base/
│   ├── simulators/
│   ├── disturbances/
│   └── scenarios/
│
├── digital_twin/
│   ├── mechanistic/
│   ├── surrogate/
│   ├── calibration/
│   └── uncertainty/
│
├── rl/
│   ├── agents/
│   ├── policies/
│   ├── rewards/
│   ├── constraints/
│   └── training/
│
├── active_learning/
│   ├── experiment_selection/
│   ├── value_of_information/
│   └── uncertainty/
│
├── llm/
│   ├── prompts/
│   ├── schemas/
│   ├── retrieval/
│   ├── agents/
│   └── knowledge_compiler/
│
├── safety/
│   ├── constraints/
│   ├── validators/
│   ├── fallback/
│   └── human_gate/
│
├── memory/
│   ├── experiences/
│   ├── retrieval/
│   └── learning/
│
├── evaluation/
│   ├── baselines/
│   ├── metrics/
│   ├── ablations/
│   ├── robustness/
│   └── benchmarks/
│
├── backend/
│   ├── api/
│   ├── services/
│   └── models/
│
├── frontend/
├── configs/
├── scripts/
├── tests/
├── docs/
├── pyproject.toml
└── README.md
```

---

# Three-Month Research Plan

TELESTO is being developed as a **focused 12-week research prototype**.

### Weeks 1–2 — Research Lock

- systematic literature review,
- prior-art mapping,
- commercial landscape,
- candidate process comparison,
- final research hypothesis.

### Weeks 2–4 — Environment

- build/adapt digital twin,
- validate dynamics,
- introduce noise and disturbances,
- introduce scale/regime shift.

### Weeks 4–5 — Baselines

- PID/MPC,
- Bayesian optimization where appropriate,
- PPO,
- SAC,
- domain-specific baseline.

### Weeks 5–7 — TELESTO Core

- state estimation,
- uncertainty,
- regime detection,
- policy adaptation,
- decision between control / measure / experiment / wait / escalate.

### Weeks 7–8 — Active Information

- measurement budget,
- experiment-selection policy,
- value-of-information evaluation.

### Weeks 8–9 — LLM Integration

- SOP/process-note ingestion,
- structured knowledge extraction,
- evidence-linked constraints,
- LLM-ablation experiments.

### Weeks 9–10 — Safety + Memory

- constraint gates,
- fallback policies,
- human escalation,
- experience memory.

### Weeks 10–11 — Evaluation

- distribution-shift tests,
- unseen-scale tests,
- equipment changes,
- noise,
- robustness,
- ablations.

### Week 12 — Research Release

- reproducible benchmark,
- final experiments,
- technical report,
- architecture documentation,
- research demo.

---

# Project Status

> **Status: Phase 0 — Research and architecture definition**

Current repository contents are **process-agnostic**.

No biological process has been permanently selected.

No validated biological model, real production-control logic, or biological deployment claim is currently implied by the codebase.

The repository deliberately distinguishes between:

- **Implemented**
- **Experimentally validated**
- **Under investigation**
- **Planned**

Synthetic experiments, when used, validate software or algorithmic behavior only; they do not establish biological validity.

---

# Research Principles

### 1. Do not force RL where it is unnecessary

If MPC, Bayesian optimization, a solver, or a classical controller is superior for a subproblem, use it.

### 2. Do not use an LLM where numerical reasoning is superior

LLMs provide semantic knowledge and context, not unrestricted physical control.

### 3. Safety before autonomy

Learned policies operate inside explicit constraints and fallback mechanisms.

### 4. Simulation before deployment

Major policies are first evaluated in controlled environments.

### 5. Measure uncertainty

The system must be able to recognize when its knowledge is insufficient.

### 6. Compare against strong baselines

Complexity is not evidence of superiority.

### 7. No fabricated results

Only reproduced and documented experiments are reported as results.

### 8. Reproducibility is a first-class requirement

Every result should be traceable to code, configuration, data/environment generation, model version, random seed, and evaluation protocol.

---

# Limitations and Non-Goals

## Known limitations

Potential limitations include:

- scarcity of high-quality process data,
- simulation-to-real mismatch,
- biological variability,
- imperfect mechanistic models,
- partially observable state,
- limited transferability across equipment,
- regulatory requirements,
- laboratory validation cost.

These are part of the research problem.

## Non-goals

TELESTO is **not** intended to:

- diagnose or treat patients,
- practice medicine,
- replace process engineers,
- bypass pharmaceutical validation,
- directly operate unrestricted production equipment,
- claim clinical effectiveness,
- let an LLM independently control biological equipment.

The focus is **decision intelligence for biological manufacturing and process development**.

---

# Reproducibility

Each published experiment should record, where applicable:

```text
Environment version
Dataset / generation configuration
Model architecture
Hyperparameters
Random seeds
Training budget
Evaluation protocol
Baseline configuration
Hardware
Software versions
```

Experiments should be reproducible from version-controlled configurations.

---

# Long-Term Vision

The long-term goal is a learning system that can accompany a biological process across:

```text
Laboratory
    ↓
Pilot
    ↓
Scale-up
    ↓
Manufacturing
    ↓
Continuous Learning
```

Rather than treating each stage as a separate optimization problem, TELESTO aims to learn **how process behavior changes, which knowledge transfers, where uncertainty increases, and what action or experiment is most valuable next**.

---

# Project Philosophy

> **Don't just optimize the process. Learn the process.**

> **Don't just act. Know when to act.**

> **Don't just predict uncertainty. Decide how to reduce it.**

> **Don't automate everything. Automate what can be justified.**

---

# License

License: **TBD**

---

## Research disclaimer

TELESTO is a research project. Any references to biomanufacturing, process control, reinforcement learning, LLMs, digital twins, or autonomous operation describe research objectives and system architecture, not validated production or clinical capability.
