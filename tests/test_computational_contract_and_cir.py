"""
tests/test_computational_contract_and_cir.py
============================================
Validation suite for Phase 2: Computational Contract & Unified CIR.
"""

import os
import tempfile
import numpy as np
import pytest

from hyper.research_engine.exactness import ExactnessCategory, ExactnessMode
from hyper.research_engine.contracts import ComputationalContract, ProblemContract
from hyper.research_engine.cir import (
    CIRGraph,
    CIRNode,
    DataType,
    OpType,
    workload_contract_to_cir,
)


def test_exactness_category_hierarchy():
    # Precedence: EXACT > NUMERICALLY_EQUIVALENT > APPROXIMATE > HEURISTIC
    exact = ExactnessCategory.EXACT
    num_eq = ExactnessCategory.NUMERICALLY_EQUIVALENT
    approx = ExactnessCategory.APPROXIMATE
    heur = ExactnessCategory.HEURISTIC

    assert exact.is_exact is True
    assert num_eq.is_exact is False
    assert approx.is_exact is False

    # EXACT can satisfy anything
    assert exact.validate_claim(ExactnessCategory.EXACT) is True
    assert exact.validate_claim(ExactnessCategory.NUMERICALLY_EQUIVALENT) is True

    # NUMERICALLY_EQUIVALENT cannot claim EXACT
    assert num_eq.validate_claim(ExactnessCategory.EXACT) is False
    assert num_eq.validate_claim(ExactnessCategory.NUMERICALLY_EQUIVALENT) is True

    # APPROXIMATE cannot claim NUMERICALLY_EQUIVALENT or EXACT
    assert approx.validate_claim(ExactnessCategory.EXACT) is False
    assert approx.validate_claim(ExactnessCategory.NUMERICALLY_EQUIVALENT) is False
    assert approx.validate_claim(ExactnessCategory.APPROXIMATE) is True

    # Mode conversion
    assert ExactnessMode.BIT_EXACT.to_category() == ExactnessCategory.EXACT
    assert ExactnessMode.NUMERIC_TOLERANCE.to_category() == ExactnessCategory.NUMERICALLY_EQUIVALENT


def test_computational_contract_creation_and_validation():
    contract = ComputationalContract(
        workload_id="TEST_CONTRACT_GEMM",
        description="Test Matrix Multiplication Contract",
        input_domain={
            "A": {"shape": [64, 64], "dtype": "FP32", "range": [-10.0, 10.0]},
            "B": {"shape": [64, 64], "dtype": "FP32", "range": [-10.0, 10.0]},
        },
        output_domain={"C": {"shape": [64, 64], "dtype": "FP32"}},
        exactness_category=ExactnessCategory.NUMERICALLY_EQUIVALENT,
        tolerance_epsilon=1e-4,
        ordering_requirements="ASSOCIATIVE_PERMITTED",
        time_constraints_ms=50.0,
        memory_constraints_bytes=64 * 1024 * 1024,
    )

    assert contract.exactness_category == ExactnessCategory.NUMERICALLY_EQUIVALENT
    assert contract.latency_limit_ms == 50.0
    assert contract.memory_limit_bytes == 64 * 1024 * 1024

    # Validate inputs
    valid_inputs = {
        "A": np.random.uniform(-5.0, 5.0, (64, 64)).astype(np.float32),
        "B": np.random.uniform(-5.0, 5.0, (64, 64)).astype(np.float32),
    }
    ok, msg = contract.validate_inputs(valid_inputs)
    assert ok is True

    # Invalid input (shape mismatch)
    bad_inputs = {
        "A": np.random.uniform(-5.0, 5.0, (32, 32)).astype(np.float32),
        "B": np.random.uniform(-5.0, 5.0, (64, 64)).astype(np.float32),
    }
    ok, msg = contract.validate_inputs(bad_inputs)
    assert ok is False
    assert "shape" in msg

    # Validate outputs
    ref = valid_inputs["A"] @ valid_inputs["B"]
    candidate_exact = ref.copy()
    candidate_noisy = ref + 1e-5
    candidate_bad = ref + 1.0

    ok_e, _, _ = contract.validate_output(candidate_exact, ref)
    assert ok_e is True

    ok_n, _, err_n = contract.validate_output(candidate_noisy, ref)
    assert ok_n is True
    assert err_n <= 1e-4

    ok_b, _, _ = contract.validate_output(candidate_bad, ref)
    assert ok_b is False


def test_computational_contract_serialization_roundtrip():
    contract = ComputationalContract(
        workload_id="TEST_SERIALIZATION",
        description="Roundtrip Contract Serialization",
        input_domain={"X": {"shape": [10, 10], "dtype": "FP32"}},
        output_domain={"Y": {"shape": [10, 10], "dtype": "FP32"}},
        exactness_category=ExactnessCategory.EXACT,
        tolerance_epsilon=0.0,
    )

    json_str = contract.to_json()
    loaded = ComputationalContract.from_json(json_str)

    assert loaded.workload_id == "TEST_SERIALIZATION"
    assert loaded.exactness_category == ExactnessCategory.EXACT
    assert loaded.tolerance_epsilon == 0.0
    assert loaded.get_contract_hash() == contract.get_contract_hash()

    # ProblemContract backward compatibility alias
    assert issubclass(ProblemContract, ComputationalContract) or ProblemContract is ComputationalContract


def test_cir_workload_export_import_and_metrics():
    contract = ComputationalContract(
        workload_id="WORKLOAD_TEST_EXPORT",
        description="Workload CIR Export Test",
        input_domain={
            "A": {"shape": [32, 32], "dtype": "FP32"},
            "B": {"shape": [32, 32], "dtype": "FP32"},
        },
        output_domain={"C": {"shape": [32, 32], "dtype": "FP32"}},
    )

    cir = workload_contract_to_cir(contract)
    assert cir.name == "WORKLOAD_TEST_EXPORT"
    assert cir.contract is not None
    assert cir.contract["workload_id"] == "WORKLOAD_TEST_EXPORT"

    # Data movement & peak memory
    data_movement = cir.calculate_total_data_movement()
    assert data_movement > 0

    peak_mem = cir.calculate_peak_live_memory()
    assert peak_mem > 0

    with tempfile.TemporaryDirectory() as tmpdir:
        cir_path = os.path.join(tmpdir, "workload.cir.json")
        cir.export_workload_cir(cir_path)
        assert os.path.exists(cir_path)

        loaded_cir = CIRGraph.import_workload_cir(cir_path)
        assert loaded_cir.name == "WORKLOAD_TEST_EXPORT"
        assert loaded_cir.contract["workload_id"] == "WORKLOAD_TEST_EXPORT"
        assert len(loaded_cir.nodes) == len(cir.nodes)
        assert loaded_cir.get_hash() == cir.get_hash()
