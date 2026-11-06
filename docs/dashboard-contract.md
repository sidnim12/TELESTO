# Observatory data contract — v1.0

React consumes the same artifact shapes in bundled and API modes. Runtime schemas
in `apps/dashboard/src/data.ts` validate responses before rendering. Requests have
a ten-second timeout and are cancelled when sources/runs change. Failed sources
are visible and never silently replaced with demo data.

| Resource | Static location | API route |
| --- | --- | --- |
| Workspace | `/demo/workspace.json` | `/api/v1/workspace` |
| Run | `/demo/runs/{id}.json` | `/api/v1/runs/{id}` |

## Workspace

`schemaVersion` is `"1.0"`; `name` and `description` identify the workspace.
`phases` is non-empty; `runs` and `evidence` may be empty. A phase looks like:

```json
{
  "id": "control", "number": "02", "title": "Control baselines",
  "status": "planned", "summary": "Compare recipe, PID, and MPC.",
  "exitCriterion": "Controllers share a reproducible evaluation protocol.",
  "milestones": [{"label": "PID evaluation", "status": "planned"}]
}
```

Phase/milestone statuses: `complete`, `active`, `planned`. Phase IDs are unique.
Run registry entries contain `id`, `label`, `phaseId`, integer `seed`, and `kind`.
Run IDs are unique; `phaseId` must reference a phase. Identifiers use only letters,
digits, underscores, and hyphens. Evidence contains `title`, `detail`, `source`
(a repository reference displayed as text), and `status`: `verified`, `pending`,
or `limitation`. This records research status, not live CI results.

## Run

Illustrative shape only; these example numbers are not research results:

```json
{
  "schemaVersion": "1.0", "id": "pid-seed-42", "label": "PID baseline",
  "seed": 42, "simulator": "IndPenSim", "generatedAt": "2026-10-21T12:00:00Z",
  "provenance": "Describe source revision, flags, and evaluation protocol.",
  "channels": [
    {"key": "tracking_error", "label": "Tracking error", "unit": "g/L", "role": "state"}
  ],
  "samples": [{"time": 0, "tracking_error": 0.3}, {"time": 0.2, "tracking_error": 0.2}]
}
```

Times are elapsed simulated hours and strictly increasing. At least two samples
are required. Every row contains finite values for `time` and all channels.
Channel keys are unique and cannot be `time`. Roles are `state` (internal) or
`observation`. New channels automatically appear in the selector and snapshot
cards using their provided labels/units. CSV columns use channel keys.

## Add Phase 2, 3, 4, or later results

1. Implement and validate the scientific work behind the existing process boundary.
2. Update phase status, milestones, and evidence in `configs/dashboard.json`.
3. Write a real result matching this contract to the artifact directory's `runs/`.
4. Add its registry entry to `workspace.json` and to `configs/dashboard.json` if
   the generator should preserve it as a standard run.
5. Refresh the browser. Published results on the roadmap open the run in Digital twin.

`python -m scripts.export_dashboard --seed 42` refreshes the bundled registry from
configuration and retains prior runs whose artifact files exist. For remote
sources, update the registry and run artifacts together. The current UI explores
single runs. Controller comparisons or decision workflows can be new React views
without changing the simulator wrapper. Keep future execution endpoints behind
orchestration and safety gates, separate from this read-only service.
