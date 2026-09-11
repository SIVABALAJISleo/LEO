"""
tests/test_cheapest_valid_path.py
=================================
Unit tests for Mechanism 9: Adaptive Cheapest-Valid-Path Engine.
Verifies the complete end-to-end pipeline and strict compliance with the required output schema.
"""

import pytest
import numpy as np
from hyper_cco.contract import ComputeContract, ExactnessClass, CorrectnessTaxonomy
from hyper_cco.cheapest_valid_path import (
    AdaptiveCheapestValidPathEngine,
    EngineExecutionReport
)


def test_cheapest_valid_path_gemm_execution():
    engine = AdaptiveCheapestValidPathEngine()
    contract = ComputeContract(
        workload_id="CHEAPEST_PATH_GEMM",
        exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
        max_absolute_error=1e-3
    )

    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)

    # 1. First execution (cold)
    out1, rep1 = engine.execute_matrix_multiplication(A, B, contract)

    assert rep1.contract_satisfied is True
    assert rep1.proof_available is True
    assert len(rep1.provenance_id) == 64
    assert rep1.classification in [c.value for c in CorrectnessTaxonomy]

    ref1 = A @ B
    assert np.allclose(out1, ref1, atol=1e-3)

    # 2. Second execution with temporal reuse (cached)
    out2, rep2 = engine.execute_matrix_multiplication(
        A=A,
        B=B,
        contract=contract,
        A_prev=A,
        B_prev=B,
        C_prev=out1
    )

    assert rep2.contract_satisfied is True
    assert rep2.work_eliminated >= 0.90
    assert rep2.classification == CorrectnessTaxonomy.CACHED.value
    assert np.allclose(out2, ref1, atol=1e-5)


def test_report_schema_compliance():
    engine = AdaptiveCheapestValidPathEngine()
    contract = ComputeContract(
        workload_id="SCHEMA_TEST",
        max_absolute_error=1e-2
    )

    A = np.eye(16, dtype=np.float32)
    B = np.eye(16, dtype=np.float32)

    _, rep = engine.execute_matrix_multiplication(A, B, contract)
    d = rep.to_dict()

    required_keys = [
        "selected_path",
        "classification",
        "estimated_cost",
        "actual_cost",
        "error",
        "contract_satisfied",
        "proof_available",
        "fallback_used",
        "speedup_vs_exact",
        "work_eliminated",
        "confidence",
        "provenance_id"
    ]

    for k in required_keys:
        assert k in d, f"Missing required key '{k}' in execution report"
        assert d[k] is not None
