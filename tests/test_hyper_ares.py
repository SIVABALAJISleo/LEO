"""
tests/test_hyper_ares.py
=============================================================================
Unit & Integration Tests for HYPER-ARES Engine
=============================================================================
"""

import pytest
import numpy as np
from hyper_ares import StructureDetector, RepresentationSearcher, PredictiveResidualEngine, HyperAresEngine

def test_structure_detector_symmetry_and_rank():
    detector = StructureDetector()
    
    # 1. Symmetric low-rank matrix
    N = 64
    r = 4
    U = np.random.randn(N, r).astype(np.float32)
    A_low_rank = U @ U.T
    
    profile = detector.analyze_matrix(A_low_rank)
    assert profile.is_square is True
    assert profile.is_symmetric is True
    assert profile.has_low_rank_structure is True
    assert "LOW_RANK_SVD" in profile.recommended_representations

def test_structure_detector_sparsity():
    detector = StructureDetector()
    N = 64
    A_sparse = np.zeros((N, N), dtype=np.float32)
    A_sparse[::4, ::4] = 1.0
    
    profile = detector.analyze_matrix(A_sparse)
    assert profile.has_sparse_structure is True
    assert "SPARSE_CSR" in profile.recommended_representations

def test_representation_searcher_matrix_candidates():
    searcher = RepresentationSearcher()
    detector = StructureDetector()
    
    A = np.random.randn(64, 64).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)
    profile = detector.analyze_matrix(A)
    
    candidates = searcher.search_matrix_representations(A, B, profile)
    assert len(candidates) >= 4
    cand_names = [c.name for c in candidates]
    assert "DENSE_AVX2" in cand_names
    assert "LOW_RANK_SVD" in cand_names
    assert "UNIVERSAL_RESIDUAL" in cand_names
    assert "MORTON_Z_CURVE" in cand_names

def test_predictive_residual_engine():
    engine = PredictiveResidualEngine(rank=16)
    N = 64
    U = np.random.randn(N, 8).astype(np.float32)
    V = np.random.randn(8, N).astype(np.float32)
    A = (U @ V) + (np.random.randn(N, N).astype(np.float32) * 0.001)
    B = np.random.randn(N, N).astype(np.float32)
    
    res = engine.solve_matrix_residual(A, B, tolerance_epsilon=0.05)
    assert res.output.shape == (N, N)
    assert res.total_cost_ms > 0
    assert res.work_elimination_ratio > 0

def test_hyper_ares_full_matrix_loop():
    engine = HyperAresEngine()
    N = 128
    U = np.random.randn(N, 16).astype(np.float32)
    V = np.random.randn(16, N).astype(np.float32)
    A = (U @ V) + (np.random.randn(N, N).astype(np.float32) * 0.005)
    B = np.random.randn(N, N).astype(np.float32)
    
    result = engine.execute_matrix_multiplication(A, B, {"epsilon": 0.05, "max_latency_ms": 100.0})
    assert result.output.shape == (N, N)
    assert len(result.candidate_benchmarks) >= 3
    assert result.verification.metric_b_contract_attainment is True
