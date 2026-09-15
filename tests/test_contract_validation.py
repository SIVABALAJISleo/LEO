"""
tests/test_contract_validation.py
=================================
Validates Phase 3 formal contract construction, validation rules,
and JSON serialization.
"""

import pytest
from hyper.contracts.contract import (
    Contract,
    contract_from_json,
    contract_to_json,
    validate_contract,
)


def test_valid_contract():
    c = Contract(
        name="ValidContract",
        exact_required=True,
        max_abs_error=0.0,
        max_relative_error=0.0,
        max_rmse=0.0,
        min_psnr=None,
        min_ssim=None,
        min_accuracy=None,
        min_recall=None,
        max_latency_ms=25.0,
        min_throughput=None,
        max_memory_bytes=None,
        allow_cache=True,
        allow_prediction=False,
        allow_approximation=False,
        allow_perceptual_difference=False,
    )
    assert validate_contract(c) is True


def test_reject_exact_with_approximation():
    c = Contract(
        name="ContradictoryContract",
        exact_required=True,
        max_abs_error=0.01,
        max_relative_error=None,
        max_rmse=None,
        min_psnr=None,
        min_ssim=None,
        min_accuracy=None,
        min_recall=None,
        max_latency_ms=None,
        min_throughput=None,
        max_memory_bytes=None,
        allow_cache=True,
        allow_prediction=False,
        allow_approximation=True,  # Contradiction with exact_required=True
        allow_perceptual_difference=False,
    )
    with pytest.raises(ValueError, match="contradictory"):
        validate_contract(c)


def test_reject_negative_error_bounds():
    c = Contract(
        name="NegativeErrorContract",
        exact_required=False,
        max_abs_error=-0.05,  # Invalid
        max_relative_error=None,
        max_rmse=None,
        min_psnr=None,
        min_ssim=None,
        min_accuracy=None,
        min_recall=None,
        max_latency_ms=None,
        min_throughput=None,
        max_memory_bytes=None,
        allow_cache=True,
        allow_prediction=True,
        allow_approximation=True,
        allow_perceptual_difference=False,
    )
    with pytest.raises(ValueError, match="max_abs_error must be non-negative"):
        validate_contract(c)


def test_reject_out_of_bounds_ssim():
    c = Contract(
        name="InvalidSSIMContract",
        exact_required=False,
        max_abs_error=None,
        max_relative_error=None,
        max_rmse=None,
        min_psnr=None,
        min_ssim=1.5,  # SSIM must be <= 1.0
        min_accuracy=None,
        min_recall=None,
        max_latency_ms=None,
        min_throughput=None,
        max_memory_bytes=None,
        allow_cache=True,
        allow_prediction=False,
        allow_approximation=True,
        allow_perceptual_difference=True,
    )
    with pytest.raises(ValueError, match="min_ssim must be within"):
        validate_contract(c)


def test_reject_out_of_bounds_accuracy():
    c = Contract(
        name="InvalidAccuracyContract",
        exact_required=False,
        max_abs_error=None,
        max_relative_error=None,
        max_rmse=None,
        min_psnr=None,
        min_ssim=None,
        min_accuracy=-0.1,  # Accuracy must be >= 0.0
        min_recall=None,
        max_latency_ms=None,
        min_throughput=None,
        max_memory_bytes=None,
        allow_cache=True,
        allow_prediction=True,
        allow_approximation=True,
        allow_perceptual_difference=False,
    )
    with pytest.raises(ValueError, match="min_accuracy must be within"):
        validate_contract(c)


def test_contract_json_serialization_roundtrip():
    c = Contract(
        name="SerializationTest",
        exact_required=False,
        max_abs_error=0.01,
        max_relative_error=0.05,
        max_rmse=0.005,
        min_psnr=35.0,
        min_ssim=0.95,
        min_accuracy=0.90,
        min_recall=0.85,
        max_latency_ms=15.0,
        min_throughput=100.0,
        max_memory_bytes=1024 * 1024 * 512,
        allow_cache=True,
        allow_prediction=True,
        allow_approximation=True,
        allow_perceptual_difference=True,
    )
    js = contract_to_json(c)
    restored = contract_from_json(js)
    assert restored.name == c.name
    assert restored.min_ssim == c.min_ssim
    assert restored.max_memory_bytes == c.max_memory_bytes
