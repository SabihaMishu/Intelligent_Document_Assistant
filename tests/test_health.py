"""Tests for the /health endpoint."""

from fastapi.testclient import TestClient


def test_health_returns_200(client: TestClient) -> None:
    """Health endpoint should respond with HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_body(client: TestClient) -> None:
    """Health endpoint should return expected fields and values."""
    response = client.get("/health")
    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "AI Engineering Document Assistant"
    assert "version" in data
    assert "environment" in data


def test_root_redirects_to_docs_info(client: TestClient) -> None:
    """Root endpoint should expose helpful links."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["health"] == "/health"
    assert data["docs"] == "/docs"
