"""
tests/test_semantic_compression.py
==================================
Unit tests for Mechanism 5: Semantic Intermediate Compression.
"""

import pytest
import numpy as np
from hyper_cco.semantic_compression import (
    SemanticCompressionEngine,
    SemanticTier,
    SemanticAllocation
)


def test_decision_critical_preserved_full_precision():
    engine = SemanticCompressionEngine()
    t = np.random.randn(10, 10).astype(np.float32)

    alloc = engine.classify_intermediate(
        tensor=t,
        downstream_gradient_norm=10.0,
        is_control_flow=True
    )

    assert alloc.tier == SemanticTier.DECISION_CRITICAL
    assert alloc.bit_width == 32

    comp, metrics = engine.compress_and_evaluate("control_tensor", t, alloc)
    assert metrics.measured_error == 0.0
    assert metrics.compression_ratio == 1.0


def test_sensitivity_critical_int8_quantization():
    engine = SemanticCompressionEngine()
    t = np.linspace(0.0, 10.0, 1000).astype(np.float32)

    alloc = engine.classify_intermediate(
        tensor=t,
        downstream_gradient_norm=0.5
    )

    assert alloc.tier == SemanticTier.SENSITIVITY_CRITICAL
    assert alloc.bit_width == 8

    comp, metrics = engine.compress_and_evaluate("dense_layer_act", t, alloc)
    assert metrics.memory_saved_bytes > 0
    assert metrics.measured_error < 0.10  # Quantization error bounded


def test_discardable_intermediate():
    engine = SemanticCompressionEngine()
    t = np.ones((50, 50), dtype=np.float32)

    alloc = engine.classify_intermediate(
        tensor=t,
        downstream_gradient_norm=0.001
    )

    assert alloc.tier == SemanticTier.DISCARDABLE
    assert alloc.storage_lifetime_s == 0.0
