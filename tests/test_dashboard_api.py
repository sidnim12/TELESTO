"""Verify artifact routes, boundaries and error behavior without running a simulator."""

import json
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient

from apps.api.main import create_app

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def client():
    return TestClient(create_app())


def test_real_workspace_and_trajectory(client):
    workspace = client.get("/api/v1/workspace")
    assert workspace.status_code == 200
    assert workspace.json()["schemaVersion"] == "1.0"
    result = client.get("/api/v1/runs/baseline-seed-42")
    assert result.status_code == 200
    assert len(result.json()["samples"]) == 1150
    assert result.json() == json.loads(
        (ROOT / "apps/dashboard/public/demo/runs/baseline-seed-42.json").read_text()
    )


def test_unknown_run_and_actuator_writes_rejected(client):
    assert client.get("/api/v1/runs/not-registered").status_code == 404
    assert client.get("/api/v1/runs/%2E%2E%5Csecret").status_code == 404
    assert client.post("/api/v1/runs/baseline-seed-42", json={"feed": 50}).status_code == 405
    assert client.post("/api/v1/control", json={"feed": 50}).status_code == 404


def test_missing_and_malformed_artifacts_have_actionable_errors(tmp_path):
    isolated = TestClient(create_app(tmp_path))
    assert isolated.get("/api/v1/workspace").status_code == 404
    (tmp_path / "workspace.json").write_text("not json")
    assert isolated.get("/api/v1/workspace").status_code == 503


def test_cors_allows_local_preview_only(client):
    allowed = client.get("/api/v1/health", headers={"Origin": "http://127.0.0.1:5173"})
    assert allowed.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
    denied = client.get("/api/v1/health", headers={"Origin": "https://unrelated.example"})
    assert "access-control-allow-origin" not in denied.headers


def test_dissolved_oxygen_units_match_simulator_metadata():
    from biocontrolos.process.fermentation.adapter import FermentationAdapter

    # Metadata lookup doesn't need a costly batch simulation.
    adapter = object.__new__(FermentationAdapter)
    assert adapter.get_sensor_definitions()["dissolved_oxygen"]["unit"] == "mg/L"
