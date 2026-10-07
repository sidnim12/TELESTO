# Assumptions and decisions

## Confirmed

- TELESTO is a research platform, not a production control system.
- Fed-batch microbial fermentation is selected as the initial research domain.
- IndPenSim / PenSimPy is the initial simulation testbed, accessed through a
  TELESTO-owned `ProcessAdapter` rather than coupled directly to the autonomy
  engine.
- Initial results are simulation studies. They do not establish biological,
  laboratory, manufacturing, clinical, or regulatory validity.
- Measurements have cost and can be selected as actions.
- Human approval is required for uncertainty- or risk-triggered escalation.

## Explicitly deferred

The research domain is selected, but the following remain evidence-dependent
and must not be invented:

- the final production organism, strain, product, and facility
- changes to published mechanistic equations or parameter values
- mappings from simulated variables to a future physical process
- validated sensor and actuator definitions/ranges
- quality attributes and acceptance criteria for a real process
- process-specific safety and equipment limits
- reward-objective weights and economics
- laboratory/plant data sources, validation protocol, and deployment pathway

## Initial technical choices

- Python 3.11+ for the scientific core.
- Standard-library-only Phase 0 contracts to keep interfaces portable.
- Immutable typed value objects where possible; modeling libraries remain intentionally deferred.
- Fermentation-specific behavior stays behind `biocontrolos/process/`; the
  state, uncertainty, decision, safety, and memory layers remain reusable.
