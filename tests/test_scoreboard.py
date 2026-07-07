"""
tests/test_scoreboard.py
Unit tests for Layer 9 Scoreboard API endpoints and calculations.
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_scoreboard_calculation():
    from backend.metrics.irrelevance_score import GPUIrrelevanceCalculator
    calc = GPUIrrelevanceCalculator()
    
    data = calc.get_10_dimension_scoreboard()
    assert "gpu_irrelevance_score" in data
    assert "dimensions" in data
    assert "reference_nvidia_baseline" in data
    
    score = data["gpu_irrelevance_score"]
    assert 0.0 <= score <= 100.0
    
    dims = data["dimensions"]
    assert len(dims) == 10
    assert dims["privacy"] == 100.0
    assert dims["offline"] == 100.0


def test_scoreboard_endpoint():
    res = client.get("/api/v1/scoreboard")
    assert res.status_code == 200
    
    data = res.json()
    assert "gpu_irrelevance_score" in data
    assert "dimensions" in data
    assert "reference_nvidia_baseline" in data
    assert isinstance(data["gpu_irrelevance_score"], float)
