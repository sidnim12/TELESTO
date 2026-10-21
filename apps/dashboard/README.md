# TELESTO Research Observatory

A React + TypeScript website for current fermentation research and future phases.
Uses React 19, Vite, Recharts, Lucide React, and Zod. Fonts are bundled locally;
the reactor is SVG/CSS. No image or animation framework is needed.

## Run the website (PowerShell)

From the repository root:

```powershell
cd apps/dashboard
npm.cmd ci
npm.cmd run dev
```

Open **http://127.0.0.1:5173**. Use Node 22.12+ or a supported newer LTS (tested
with Node 24). `npm.cmd` avoids PowerShell's `npm.ps1` execution-policy restriction.
On macOS/Linux, use `npm` instead.

Bundled mode needs **no Python server**. Its 1,150 samples are exported from the
real seed-42 simulator. The checked-in JSON makes the demo reproducible without
rerunning the simulator.

## Optional API

In a second terminal, from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[web]"
.\.venv\Scripts\python.exe -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000
```

If no virtual environment exists, first run `python -m venv .venv`.
Open **Connection settings → Connect an API**, use
`http://127.0.0.1:8000/api/v1`, and **Apply connection**. The source choice persists
in this browser. Select **Bundled simulation** to switch back. Errors are visible;
API failures are never silently replaced by demo data.

Runtime default: edit `public/config.json` (`apiBaseUrl`) without changing React
code. In a production build edit `dist/config.json`. A saved browser choice
overrides that default. API docs: http://127.0.0.1:8000/docs.

## Regenerate or add results

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m scripts.export_dashboard --seed 42
.\.venv\Scripts\python.exe -m scripts.export_dashboard --seed 43
```

The exporter preserves previously exported seeds and refreshes phases from
`configs/dashboard.json`. All samples retain their original numerical values;
only chart rendering is sampled to roughly 400 points. CSV contains every row.

To serve a different artifact directory, set `TELESTO_DATA_DIR` before starting
the API. See [the data contract](../../docs/dashboard-contract.md) for publishing
Phase 2, 3, 4, and later results. Channels, runs, milestones, and evidence are
data-driven. Multi-run overlays and controller execution are outside this UI.

## Checks and production

```powershell
npm.cmd test
npm.cmd run build
npm.cmd run preview
```

Production preview: http://127.0.0.1:4173. Serve `dist/` at a static host's domain
root; hash navigation needs no route rewrites. The optional API is separate.
Stop local servers with Ctrl+C. Format source with `npm.cmd run format`.

## Deploy to Vercel

The repository contains two equivalent Vercel configurations so either project
layout works:

1. **Recommended:** import the TELESTO repository and leave Vercel's **Root
   Directory** empty. The root `vercel.json` installs and builds
   `apps/dashboard`, then publishes `apps/dashboard/dist`.
2. If the Vercel project already uses **Root Directory** `apps/dashboard`, keep
   it. The `apps/dashboard/vercel.json` builds and publishes `dist`.

Do not set the root directory to `dist`, and do not use the Python API as the
frontend's build target. In Vercel Project Settings → Build and Deployment,
clear old custom commands so the tracked configuration can take effect, then
redeploy the latest commit. The deployment must include `vercel.json`,
`apps/dashboard/package-lock.json`, and `apps/dashboard/public/demo/`.

The deployed site defaults to bundled simulation data. A local API URL such as
`http://127.0.0.1:8000/api/v1` cannot be reached by visitors on Vercel; leave
`public/config.json` with an empty `apiBaseUrl` unless a public HTTPS API has
been deployed separately.

From the repository root, run Python checks with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Replay advances recorded samples; it does not execute CONTROL or imply Phase 1B,
PID, MPC, or RL is complete. Themes persist and respect the initial system theme.
Animations respect reduced-motion preferences.

The sidebar contains only Overview, Digital twin, Research roadmap, and Evidence
library. Its desktop toggle switches between the full menu and an icon rail,
remembering the choice locally. On mobile, the menu slides in and closes after
navigation or Escape. Connection settings are available from the source selector
in the top bar. Both light and dark themes use a blue palette; hover and press
feedback use CSS transitions without an additional animation dependency.
