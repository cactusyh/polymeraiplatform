"""Smoke tests for the public Phase 1 endpoints."""

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "polymer-ai-backend"}


def test_platform_info() -> None:
    response = client.get("/api/v1/info")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Polymer AI Platform",
        "version": "0.1.0",
        "status": "development",
    }
