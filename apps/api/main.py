"""Read-only observatory API. No simulator execution or actuator routes."""

import json
import os
from pathlib import Path
import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[2]


def create_app(data_dir: Path | None = None) -> FastAPI:
    directory = (data_dir or Path(os.environ.get("TELESTO_DATA_DIR", ROOT / "apps/dashboard/public/demo"))).resolve()
    app = FastAPI(title="TELESTO Observatory", version="1.0", description="Read-only research artifacts. No actuator authority.")
    origins = os.environ.get("TELESTO_CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:4173").split(",")
    app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in origins], allow_methods=["GET"], allow_headers=["Accept"])

    def read_artifact(relative: str) -> dict:
        target = (directory / relative).resolve()
        if not target.is_relative_to(directory):
            raise HTTPException(404, "Artifact not found")
        try:
            artifact = json.loads(target.read_text(encoding="utf-8"))
            if not isinstance(artifact, dict) or artifact.get("schemaVersion") != "1.0":
                raise ValueError("Unsupported artifact schema")
            return artifact
        except FileNotFoundError:
            raise HTTPException(404, "Artifact not found. Export dashboard data first.") from None
        except (ValueError, OSError):
            raise HTTPException(503, "Artifact is unavailable or invalid.") from None

    @app.get("/api/v1/health")
    def health():
        return {"status": "ok", "schemaVersion": "1.0", "mode": "read-only"}

    @app.get("/api/v1/workspace")
    def workspace():
        return read_artifact("workspace.json")

    @app.get("/api/v1/runs/{run_id}")
    def run(run_id: str):
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", run_id):
            raise HTTPException(404, "Run not found")
        registry = read_artifact("workspace.json")
        if not any(r.get("id") == run_id for r in registry.get("runs", [])):
            raise HTTPException(404, "Run not found")
        return read_artifact(f"runs/{run_id}.json")

    return app


app = create_app()
