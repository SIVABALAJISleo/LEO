"""
tests/test_local_inference_product.py
=====================================
Tests for Phase 6: Real Local AI Inference Product.
Verifies genuine local GGUF execution, token generation, TTFT, throughput measurement,
and strictly local execution without cloud or external services.
"""

import os
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.routers.inference_router import DEFAULT_MODEL_PATH, _HAS_LLAMA_CPP

client = TestClient(app)

_HAS_LOCAL_MODEL = os.path.exists(DEFAULT_MODEL_PATH) and _HAS_LLAMA_CPP
skip_without_model = pytest.mark.skipif(
    not _HAS_LOCAL_MODEL,
    reason="Local GGUF model not present on disk in clean CI runner.",
)


def test_inference_model_info():
    """Verify local GGUF model discovery and metadata endpoint."""
    response = client.get("/api/v1/inference/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["format"] == "GGUF"
    assert data["quantization"] == "Q4_K_M"
    assert data["model_name"] == "Qwen2.5-0.5B-Instruct-Q4_K_M"
    assert data["is_local_only"] is True
    assert data["cloud_compute_used"] is False
    assert data["paid_api_required"] is False
    if _HAS_LOCAL_MODEL:
        assert data["is_model_present_on_disk"] is True
        assert data["file_size_mb"] > 400


@skip_without_model
def test_inference_real_generation():
    """Verify real local token generation with measured TTFT and throughput."""
    req_payload = {
        "prompt": "Hello world",
        "max_tokens": 16,
        "temperature": 0.7,
        "top_p": 0.9,
        "seed": 42,
    }
    response = client.post("/api/v1/inference/generate", json=req_payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["text"]) > 0
    assert data["tokens_generated"] > 0
    assert data["time_to_first_token_ms"] > 0
    assert data["generation_throughput_tokens_per_sec"] > 0
    assert data["total_latency_ms"] > 0
    assert data["provenance"] == "MEASURED"
    assert data["is_local_only"] is True
    assert "Host CPU" in data["device"]
    assert data["backend"] == "LLAMA_CPP_CPU_AVX2"


@skip_without_model
def test_inference_benchmark_endpoint():
    """Verify inference benchmark execution across multiple trials."""
    req_payload = {
        "prompt": "Compute 2 + 2.",
        "max_tokens": 12,
        "iterations": 2,
    }
    response = client.post("/api/v1/inference/benchmark", json=req_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PASS"
    assert data["provenance"] == "MEASURED"
    assert data["iterations"] == 2
    assert data["median_time_to_first_token_ms"] > 0
    assert data["median_generation_throughput_tokens_per_sec"] > 0
    assert len(data["raw_samples"]["ttft_ms"]) == 2
    assert len(data["raw_samples"]["tokens_per_sec"]) == 2
    assert data["discrete_gpu_used"] is False
    assert data["cloud_service_used"] is False


@skip_without_model
def test_inference_streaming_sse_endpoint():
    """Verify Server-Sent Events (SSE) streaming output from /api/v1/inference/generate."""
    import json

    req_payload = {
        "prompt": "State one law of thermodynamics.",
        "max_tokens": 10,
        "temperature": 0.5,
        "stream": True,
    }
    response = client.post("/api/v1/inference/generate", json=req_payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")

    lines = [line.strip() for line in response.text.split("\n") if line.strip()]
    assert len(lines) >= 3

    data_lines = [l for l in lines if l.startswith("data:")]
    assert len(data_lines) >= 2
    assert data_lines[-1] == "data: [DONE]"

    # Validate first token chunk
    first_chunk = json.loads(data_lines[0].replace("data:", "").strip())
    assert "choices" in first_chunk or "token" in first_chunk
    assert first_chunk.get("done") is False

    # Validate final metadata chunk
    penultimate_chunk = json.loads(data_lines[-2].replace("data:", "").strip())
    assert penultimate_chunk.get("done") is True
    assert "x_leo_metadata" in penultimate_chunk
    assert penultimate_chunk["x_leo_metadata"]["local_only"] is True
    assert penultimate_chunk["x_leo_metadata"]["provenance"] == "MEASURED"


@skip_without_model
def test_inference_stream_alias_endpoint():
    """Verify dedicated alias /api/v1/inference/stream endpoint."""
    import json

    req_payload = {
        "prompt": "Hello",
        "max_tokens": 6,
    }
    response = client.post("/api/v1/inference/stream", json=req_payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")
    assert "data: [DONE]" in response.text

