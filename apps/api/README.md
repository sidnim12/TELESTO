# TELESTO Observatory API

Read-only FastAPI service for versioned research artifacts. No action, controller,
simulator-execution, or actuator endpoint.

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[web]"
.\.venv\Scripts\python.exe -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000
```

- `GET /api/v1/health`: service health and read-only mode.
- `GET /api/v1/workspace`: phase, run, and evidence registry.
- `GET /api/v1/runs/{id}`: a registered run's channels and trajectory.
- `/docs`: generated OpenAPI documentation.

`TELESTO_DATA_DIR` overrides the artifact directory; default:
`apps/dashboard/public/demo`. Files are read per request, so replacing them needs
no restart. The exporter replaces files atomically. `TELESTO_CORS_ORIGINS` is a
comma-separated allowlist; defaults permit the local frontend origins.
This is a local service without auth; bind to loopback or add authentication at
your deployment boundary.

See [dashboard instructions](../dashboard/README.md) and
[the data contract](../../docs/dashboard-contract.md).
