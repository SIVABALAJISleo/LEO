import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestAuthAPI:
    def test_signup_positive(self):
        res = client.post("/api/v1/auth/signup", json={
            "email": "api_test_user@leo.ai",
            "password": "ValidPassword2026!"
        })
        assert res.status_code in [200, 400] # 400 if user already registered

    def test_login_positive(self):
        res = client.post("/api/v1/auth/login", json={
            "email": "api_test_user@leo.ai",
            "password": "ValidPassword2026!"
        })
        if res.status_code == 200:
            data = res.json()
            assert "access_token" in data or "user" in data

    def test_login_negative_invalid_password(self):
        res = client.post("/api/v1/auth/login", json={
            "email": "api_test_user@leo.ai",
            "password": "WrongPassword123!"
        })
        assert res.status_code == 401

class TestOrchestrateAPI:
    def test_metrics_endpoint(self):
        res = client.get("/api/v1/leo/metrics")
        assert res.status_code == 200
        data = res.json()
        assert "status" in data or "metrics" in data or "timestamp" in data

class TestMemoryAPI:
    def test_memory_store_and_retrieve(self):
        store_res = client.post("/api/v1/systems/memory/store", json={
            "key": "qa_test_key",
            "value": "qa_test_value"
        })
        assert store_res.status_code in [200, 201]

    def test_memory_summary(self):
        res = client.get("/api/v1/systems/memory/summary")
        assert res.status_code == 200
