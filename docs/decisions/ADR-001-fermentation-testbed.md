# ADR-001: Fed-batch fermentation research testbed

- **Status:** Accepted
- **Date:** 2026-10-07
- **Decision owners:** TELESTO research team

## Context

TELESTO needs a concrete process world before control, uncertainty, adaptation,
information acquisition, and cross-batch learning can be evaluated. The Phase 0
architecture was deliberately process-agnostic, but an executable testbed is
now required to make the research hypotheses falsifiable.

The initial domain must provide nonlinear and time-dependent dynamics,
partially observed state, multiple manipulated and measured variables,
batch-to-batch variation, operating constraints, disturbances, and long-horizon
outcomes. It must also support repeatable offline experiments without exposing a
physical process to experimental control policies.

## Decision

Use **fed-batch microbial fermentation** as TELESTO's initial research domain.
Use **IndPenSim**, through a maintained **PenSimPy** implementation where
practical, as the first simulation testbed.

The simulator will be wrapped by a TELESTO-owned adapter under
`biocontrolos/process/`. No controller, policy, agent, or LLM may depend directly
on IndPenSim/PenSimPy types. This preserves the process boundary and allows the
testbed to be replaced without rewriting the autonomy engine.

## Rationale

IndPenSim was published as an industrial-scale fed-batch penicillin fermentation
benchmark for process-systems and control research. It provides mechanistic,
multivariable batch dynamics and supports experiments involving process
measurements, control strategies, variability, and faults. PenSimPy makes that
testbed accessible from the Python scientific stack used by TELESTO.

This choice gives the project a sufficiently rich and reproducible environment
for testing its decision architecture while retaining a clear separation
between simulated evidence and operation of a real biological process.

## Scientific claims permitted

Results may support claims about:

- TELESTO software behavior on the specified simulator and version;
- relative controller or policy performance under documented simulated scenarios;
- uncertainty calibration and regime-shift detection in those scenarios;
- the simulated value of measurements, experiments, memory, or counterfactual planning;
- reproducibility across declared seeds, configurations, and evaluation splits.

## Scientific claims not permitted

Results must not be presented as evidence of:

- biological validity outside the model's documented scope;
- successful transfer to another organism, strain, product, reactor, or scale;
- validated physical scale-up or scale-down behavior;
- safe or effective laboratory, pilot, clinical, or manufacturing control;
- regulatory compliance, product-quality assurance, or production readiness;
- superiority on real equipment without independent experimental validation.

The words *industrial-scale* describe the published simulator's modeled case;
they do not mean that TELESTO has been validated on an industrial facility.

## Consequences

- Phase 1 becomes environment integration and validation, before RL or LLM work.
- Fermentation-specific variables and equations remain inside the process adapter.
- Simulator provenance, version, license, configuration, and any local changes
  must be recorded for every experiment.
- TELESTO must retain deterministic seeded scenarios and tests that compare the
  adapter with direct simulator outputs.
- A future physical process requires a new adapter and a separate validation and
  safety decision.

## Sources

- Goldrick et al., *The development of an industrial-scale fed-batch
  fermentation simulation*, Journal of Biotechnology 193 (2015), 70–82,
  DOI: https://doi.org/10.1016/j.jbiotec.2014.10.029
- IndPenSim source repository:
  https://github.com/Lemniscabio/IndPenSim
- PenSimPy source repository:
  https://github.com/Mohan-Zhang-u/PenSimPy
