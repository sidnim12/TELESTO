# Workspace review for the observatory

Reviewed application boundaries, Python interfaces and tests, configuration,
research docs, scripts, simulator integration, external simulator structure and
channel metadata, and the existing figure artifact. Virtual environments,
dependency caches, Git internals, and generated binaries are not application
source. One old pytest cache directory was inaccessible.

| Area | State when reviewed | Observatory use |
| --- | --- | --- |
| `process/fermentation` | Working batch wrapper and WAIT replay | Actual seeded trajectory exports |
| `process/base` | Generic process contracts | Preserve the process boundary |
| Core, twin, agent, memory, safety contracts | Typed interfaces / abstract contracts | Show architecture without claiming implemented intelligence |
| Control, RL, most agents/twins/memory | Reserved placeholders | Planned phases, no fake performance metrics |
| `docs` | Roadmap, progress, assumptions, provenance | Phase and evidence registry |
| Baseline TOML | Experimental record, not runtime-loaded | Wrapper defaults, not a claim of TOML execution |
| `scripts` | Smoke, batch, trajectory plot | Added repeatable JSON export |
| `apps` | Placeholder boundaries | Read-only API and React observatory |
| `data`, `experiments` | Empty scaffolding | No invented experiments |
| External simulator | Local IndPenSim translation | Retained unchanged |
| `outputs/figures` | Baseline trajectory PNG | Existing independent visualization |

- Phase 0 is complete; Phase 1A is validated; Phase 1B remains incomplete.
- CONTROL does not affect future states and deliberately raises NotImplementedError.
  The website explicitly presents precomputed replay.
- Upstream `DO2` specifies mg/L in `simulator/batch.py`; the adapter's `%` label
  was incorrect and is corrected with a regression check.
- No calibrated uncertainty, PID/MPC comparison, RL policy, or LLM result exists.
  Future work can publish results through the versioned data contract.
- The simulator revision/license remains unverified; signed harvested product is
  excluded from dashboard KPIs.
- Existing user edits in the root README were preserved.

See `apps/dashboard/README.md` for running and extension instructions.
