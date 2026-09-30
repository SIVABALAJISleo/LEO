import pytest
import numpy as np
from hyper_x.wormhole_compiler.optimization_applicability import OptimizationApplicabilityEngine

def test_low_rank_flat_spectrum_rejection():
    engine = OptimizationApplicabilityEngine()
    # Create a full rank matrix with a flat spectrum
    workload = np.eye(128)
    class DummyContract:
        tolerance = 1e-3
    report = engine.evaluate(workload, "test_mat", DummyContract(), "LOW_RANK")
    assert not report.applicable
    assert report.classification == "FLAT_SPECTRUM"

def test_low_rank_decaying_spectrum_acceptance():
    engine = OptimizationApplicabilityEngine()
    # Create a matrix with strong spectral decay
    U = np.random.randn(128, 16)
    V = np.random.randn(16, 128)
    workload = U @ V
    class DummyContract:
        tolerance = 1e-3
    report = engine.evaluate(workload, "test_mat", DummyContract(), "LOW_RANK")
    assert report.applicable
    assert report.classification == "STRONG_SPECTRAL_DECAY"

def test_sparse_threshold_overhead_rejection():
    engine = OptimizationApplicabilityEngine()
    # Matrix that is mostly dense
    workload = np.random.randn(128, 128)
    class DummyContract:
        tolerance = 1e-3
    report = engine.evaluate(workload, "test_mat", DummyContract(), "THRESHOLD_SPARSITY")
    assert not report.applicable
    assert report.classification == "LOW_SPARSITY"

def test_sparse_real_sparsity_acceptance():
    engine = OptimizationApplicabilityEngine()
    # Matrix that is mostly sparse
    workload = np.zeros((128, 128))
    workload[0, 0] = 1.0
    workload[1, 1] = 1.0
    class DummyContract:
        tolerance = 1e-3
    report = engine.evaluate(workload, "test_mat", DummyContract(), "THRESHOLD_SPARSITY")
    assert report.applicable
    assert report.classification == "HIGH_SPARSITY"
