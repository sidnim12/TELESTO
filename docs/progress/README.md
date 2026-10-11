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

**Status: Baseline integration validated; interactive control incomplete**

- **Phase 1A — Baseline digital-twin integration:** complete
- **Phase 1B — Interactive/action-conditioned control interface:** incomplete

We:

- added the external IndPenSim simulator for local research use;
- created a TELESTO-owned fermentation simulator wrapper;
- isolated the external simulator under a private module namespace to prevent
  Python import conflicts;
- declared and installed NumPy and SciPy as runtime dependencies;
- added a simulator smoke test that uses the TELESTO wrapper;
- implemented the fermentation `ProcessAdapter` state, observation, reward,
  constraint, sensor, actuator, and action-validation interfaces;
- exposed biomass, substrate, penicillin, dissolved oxygen, pH, temperature,
  and volume through TELESTO-owned types;
- established a versioned seed-42 baseline configuration record;
- verified same-seed reproducibility and different-seed variation;
- added numerical data-integrity and strictly increasing time checks;
- added baseline batch and trajectory-plot scripts;
- recorded simulator provenance and known interpretation limits;
- successfully ran a complete simulated batch with 1,150 samples over 229.8
  simulated hours;
- verified the architecture and fermentation integration tests.

### Gating item before closed-loop control experiments

`WAIT` currently advances along a precomputed baseline trajectory. Although
substrate-feed, aeration, and agitation actions exist in the adapter interface,
they do not yet alter future simulator states; `transition_model()` deliberately
raises `NotImplementedError` for `CONTROL`.

Before PID, MPC, or RL comparisons begin, TELESTO must implement and test an
action-conditioned transition interface into the fermentation simulator.

Additional provenance work remains: pin the external simulator to a verified
upstream commit and license. The negative signed harvested-product statistic is
documented but must not be treated as a validated KPI.

## Later phases

Control baselines, regime shifts, uncertainty estimation, adaptive decision
policies, information acquisition, counterfactual evaluation, memory, and the
LLM knowledge interface remain planned. Closed-loop control baselines should
begin only after action-conditioned process dynamics are available.
