# Assumptions and decisions

## Confirmed

- BioControlOS is a research platform, not a production control system.
- The target biological process is not selected.
- The initial environment must be abstract and synthetic.
- Measurements have cost and can be selected as actions.
- Human approval is required for uncertainty- or risk-triggered escalation.

## Explicitly deferred

All of the following are `BIOLOGICAL_PROCESS_DECISION_REQUIRED`:

- target biological process and operating regime
- mechanistic equations and parameter values
- sensor and actuator definitions/ranges
- quality attributes and acceptance criteria
- process-specific safety limits
- reward-objective weights and economics
- real data sources, validation protocol, and deployment pathway

## Initial technical choices

- Python 3.11+ for the scientific core.
- Standard-library-only Phase 0 contracts to keep interfaces portable.
- Immutable typed value objects where possible; modeling libraries remain intentionally deferred.
