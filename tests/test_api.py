from fastapi.testclient import TestClient
from backend.main import app
import pytest

client = TestClient(app)

def test_health_check():
    """Test standard health monitor endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_root():
    """Test root entry point."""
    response = client.get("/")
    assert response.status_code == 200
    assert "LEO" in response.json()["message"]
