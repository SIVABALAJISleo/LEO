"""
tests/test_leo_runtime.py
=========================
Integration tests for Project LEO / HYPER UMA Runtime & Speculative Router.
"""

import pytest
from fastapi.testclient import TestClient

from leo_router import app, semantic_cache, speculative_engine, kv_cache_manager
from leo_falsification_watchdog import SelfFalsificationWatchdog

client = TestClient(app)


def test_leo_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "HEALTHY"
    assert "Intel Core i5-12450H" in data["hardware_target"]


def test_leo_models_endpoint():
    resp = client.get("/v1/models")
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert data["data"][0]["id"] == "leo-hyper-i5-12450h-q4"


def test_leo_status_telemetry():
    resp = client.get("/v1/leo/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "uma_memory" in data
    assert "kv_cache" in data
    assert "speculative_decoding" in data
    assert data["uma_memory"]["ram_ceiling_guard_mb"] == 12288.0


def test_leo_chat_completions_non_streaming():
    payload = {
        "model": "leo-hyper-i5-12450h-q4",
        "messages": [
            {"role": "system", "content": "You are LEO runtime."},
            {"role": "user", "content": "What is verified mathematical parity?"}
        ],
        "max_tokens": 16,
        "stream": False,
    }
    resp = client.post("/v1/chat/completions", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "choices" in data
    assert len(data["choices"]) > 0
    assert "content" in data["choices"][0]["message"]
    assert len(data["choices"][0]["message"]["content"]) > 0


def test_leo_chat_completions_semantic_cache_hit():
    user_query = "Calculate zero-copy UMA bandwidth"
    payload = {
        "model": "leo-hyper-i5-12450h-q4",
        "messages": [{"role": "user", "content": user_query}],
        "max_tokens": 16,
        "stream": False,
    }

    # 1. First call: miss & insert
    resp1 = client.post("/v1/chat/completions", json=payload)
    assert resp1.status_code == 200

    # 2. Second call: instant hit
    resp2 = client.post("/v1/chat/completions", json=payload)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2.get("system_fingerprint") == "leo_fast_semantic_cache_hit"


def test_leo_chat_completions_streaming():
    payload = {
        "model": "leo-hyper-i5-12450h-q4",
        "messages": [{"role": "user", "content": "Stream speculative tokens"}],
        "max_tokens": 8,
        "stream": True,
    }
    resp = client.post("/v1/chat/completions", json=payload)
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    text = resp.text
    assert "data:" in text
    assert "[DONE]" in text


def test_leo_falsification_watchdog_audit():
    watchdog = SelfFalsificationWatchdog()
    report = watchdog.run_comprehensive_audit()
    assert report["overall_status"] == "PASSED"
    assert report["contract_compliance"]["sub_100ms_ttft"] is True
    assert report["contract_compliance"]["exact_token_distribution"] is True
    assert report["contract_compliance"]["numerical_precision_bound"] is True
    assert report["contract_compliance"]["process_ram_under_12gb_cap"] is True
