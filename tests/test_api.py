import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "env" in data

def test_telemetry_endpoint():
    # Requires backend/routers/cpu_compute to be mounted
    response = client.get("/api/v1/compute/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert "cpu" in data
    assert "memory" in data

def test_vision_detect_endpoint_missing_file():
    # Should fail elegantly with 422 if no multipart file provided
    response = client.post("/api/v1/vision/detect")
    assert response.status_code == 422

def test_vision_segment_endpoint_missing_file():
    response = client.post("/api/v1/vision/segment")
    assert response.status_code == 422

def test_vision_caption_endpoint_missing_file():
    response = client.post("/api/v1/vision/caption")
    assert response.status_code == 422
    
def test_jepa_compare_endpoint_missing_files():
    response = client.post("/api/v1/jepa/compare")
    assert response.status_code == 422
