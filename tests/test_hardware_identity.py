"""
tests/test_hardware_identity.py
===============================
Tests Phase 2 dynamic hardware profiling and model fail-closed logic.
Ensures no hardcoded CPU identities and graceful degradation when models are missing.
"""

import pytest
from hyper.hardware import get_hardware_profile, validate_model_presence


def test_dynamic_hardware_profile():
    profile = get_hardware_profile()

    assert "os" in profile
    assert "cpu_model" in profile
    assert len(profile["cpu_model"]) > 0
    assert profile["physical_cores"] > 0
    assert profile["logical_processors"] >= profile["physical_cores"]
    assert profile["ram_total_bytes"] > 0
    assert "gpu_model" in profile
    assert "openvino_devices" in profile
    assert isinstance(profile["openvino_devices"], list)

    # Invariant: If hardware detects i5-13420H, it must NOT label it as i5-12450H
    if "13420H" in profile["cpu_model"]:
        assert "12450H" not in profile["cpu_model"]


def test_missing_model_fails_closed():
    # Missing non-existent model file
    status = validate_model_presence("/non/existent/path/to/model.onnx")

    assert status["status"] == "DEGRADED"
    assert status["model_valid"] is False
    assert status["benchmark_allowed"] is False
    assert "error" in status
