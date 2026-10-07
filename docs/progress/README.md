# TELESTO progress

This page is a simple record of what has been completed in each research phase.
Detailed scope and exit criteria remain in [`../roadmap.md`](../roadmap.md).

## Phase 0 — Architecture and research definition

**Status: Complete**

We:

- created the process-agnostic TELESTO repository structure;
- defined interfaces for process adapters, state and uncertainty estimation,
  rewards, constraints, digital twins, safety, memory, and agents;
- established that learned policies and LLMs cannot bypass the safety gate;
- selected fed-batch microbial fermentation as the initial research domain;
- documented the IndPenSim/PenSimPy testbed decision and its scientific limits;
- aligned the assumptions, architecture, and research roadmap.

## Phase 1 — Fermentation digital twin

**Status: In progress**

We:

- added the external IndPenSim simulator for local research use;
- created a TELESTO-owned fermentation simulator wrapper;
- isolated the external simulator under a private module namespace to prevent
  Python import conflicts;
- declared and installed NumPy and SciPy as runtime dependencies;
- added a simulator smoke test that uses the TELESTO wrapper;
- successfully ran a complete simulated batch with 1,150 samples over 229.8
  simulated hours;
- verified the existing architecture tests.

Still required before Phase 1 is complete:

- implement the full fermentation `ProcessAdapter` contract;
- define versioned state, observation, action, outcome, and constraint schemas;
- record simulator provenance and deterministic configuration;
- add adapter-to-simulator equivalence and reproducibility tests;
- add trajectory visualization and documented validation scenarios.

## Later phases

Control baselines, regime shifts, uncertainty estimation, adaptive decision
policies, information acquisition, counterfactual evaluation, memory, and the
LLM knowledge interface remain planned. They should begin only when the
preceding phase satisfies its documented exit criteria.
