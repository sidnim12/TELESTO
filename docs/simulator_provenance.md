# Simulator provenance

## Identity and purpose

- **Simulator:** IndPenSim V2 Python translation (`pensimpy-simulator`)
- **Local path:** `external/pensimpy-simulator/`
- **Upstream named by the local README:**
  `https://github.com/ErnstHolger/pensimpy-simulator`
- **Underlying research model:** IndPenSim industrial-scale fed-batch
  penicillin fermentation benchmark
- **Use in TELESTO:** simulation research testbed for Phase 1 integration and
  repeatability experiments

IndPenSim is used as a simulation research testbed.

TELESTO does not claim ownership of the underlying simulator.

Current results are simulated results and do not constitute laboratory,
clinical, manufacturing, or industrial validation.

## Version and license status

The local simulator directory does not contain `.git` metadata, a commit
identifier, a release tag, or a license file. Therefore:

- the exact upstream commit represented by the local copy is **unverified**;
- equivalence to the current upstream repository is **unverified**;
- the license of this exact local translation is **not identifiable from the
  checked-out files**.

The related `Mohan-Zhang-u/PenSimPy` project advertises an MIT license, but that
license must not be assumed to cover this separate local translation without
provenance evidence. Pinning an upstream source, commit, and license is required
before redistribution or release decisions.

## TELESTO integration

`biocontrolos/process/fermentation/simulator.py` loads the external simulator
under a private module namespace and converts selected channels into the
TELESTO-owned `FermentationBatch` type. It also:

- applies an optional NumPy seed while restoring the caller's random state;
- exposes time, biomass, substrate, penicillin, dissolved oxygen, pH,
  temperature, and volume;
- checks non-empty output, equal trajectory lengths, finite values, strictly
  increasing time, and positive duration.

`biocontrolos/process/fermentation/adapter.py` maps that batch into the generic
TELESTO `ProcessAdapter` interface. It does not modify the external simulator.

## Verified software environment

The Phase 1 exit review used:

- Python `3.13.14`
- NumPy `2.5.3`
- SciPy `1.18.1`
- Matplotlib `3.11.2`

Project dependency ranges remain defined in `pyproject.toml`.

## Baseline experimental record

The versioned record is `configs/fermentation_baseline.toml`:

- seed: `42`
- batch fault reference: `0`
- control strategy: `0`
- batch length mode: `0`
- Raman mode: `0`
- nominal external sample interval: `0.2 h`
- nominal external horizon: `230 h`

The TOML is currently a **versioned experimental record**, not a runtime-loaded
configuration source. Runtime defaults are defined in
`FermentationSimulator`; interface schemas, provisional actuator limits, and
relative measurement costs are defined in `FermentationAdapter`.

## Local modifications

No external simulator files were modified during the Phase 1 exit review.
Because the local copy has no Git metadata, earlier local modifications or
differences from upstream cannot be established confidently.

## Known limitations

- TELESTO runs complete batches; it does not yet provide an action-conditioned
  step interface into IndPenSim.
- `WAIT` advances through an already generated baseline trajectory.
- TELESTO `CONTROL` actions are validated structurally but do not alter future
  simulator states and deliberately raise `NotImplementedError`.
- Actuator ranges and measurement costs are provisional research-interface
  values, not validated equipment or economic limits.
- The external simulator uses built-in recipe and PID behavior internally;
  that is distinct from a TELESTO-controlled closed loop.
- With batch-length mode `1`, the external runner calls
  `np.random.seed(None)`, which bypasses deterministic TELESTO seeding. The
  Phase 1 baseline uses mode `0`.
- The external discharge channel uses negative values for outflow. Its console
  “harvested during the batch” statistic sums signed discharge times product
  concentration and therefore prints a negative value. This signed statistic
  is not a validated TELESTO KPI.
- Raman mode is disabled in the baseline and may require an external reference
  spectra file when enabled.

## Primary references

- Goldrick et al., “The development of an industrial-scale fed-batch
  fermentation simulation,” *Journal of Biotechnology* 193 (2015), 70–82.
  https://doi.org/10.1016/j.jbiotec.2014.10.029
- Local README-named translation source:
  https://github.com/ErnstHolger/pensimpy-simulator
- Related PenSimPy implementation:
  https://github.com/Mohan-Zhang-u/PenSimPy
