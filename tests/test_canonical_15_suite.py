"""
tests/test_canonical_15_suite.py
Independent Correctness Verification & Regression Suite for the 15 Canonical Workloads.
Validates:
- Phase 1: Canonical Workload Registry & Schema Enforcement
- Phase 2: Independent Reference Engine & Faulty-Candidate Rejection
- Phase 3: Candidate Compiler & Dispatch
- Phase 5: Correctness-Preserving Multi-Operand Cache
- Phase 6: Truthful Hardware Backend Detection
- Phase 7 & 8: Adversarial Verification & Fail-Closed State Machine
- Phase 11: FastAPI Canonical Workload Router Endpoints
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient

from hyper.canonical.workload_registry import (
    CanonicalWorkloadRegistry,
    CanonicalWorkloadContract,
    ExactnessClass,
    TensorSchema,
    CANONICAL_15_WORKLOAD_IDS,
    CANONICAL_REGISTRY,
)
from hyper.canonical.independent_reference import (
    IndependentReferenceEngine,
    UnsupportedWorkloadError,
)
from hyper.canonical.candidate_compiler import CandidateCompiler
from hyper.canonical.verified_cache import VerifiedExactCache, VERIFIED_CACHE
from hyper.canonical.hardware_backends import (
    HardwareBackendManager,
    HARDWARE_BACKEND,
)
from hyper.canonical.verification_state_machine import (
    StrictVerificationRunner,
    VerificationStatus,
    WorkloadVerificationRecord,
    SuiteVerificationReport,
)
from backend.main import app

client = TestClient(app)


class TestPhase1Registry:
    """Verifies that the canonical workload registry satisfies strict contract integrity."""

    def test_registry_contains_exactly_15_canonical_workloads(self):
        contracts = CANONICAL_REGISTRY.get_all_contracts()
        assert len(contracts) == 15
        assert set(contracts.keys()) == set(CANONICAL_15_WORKLOAD_IDS)

    def test_each_contract_has_valid_schema_and_exactness_class(self):
        for w_id in CANONICAL_15_WORKLOAD_IDS:
            contract = CANONICAL_REGISTRY.get(w_id)
            assert contract is not None
            assert contract.workload_id == w_id
            assert contract.exactness_class in ExactnessClass
            assert len(contract.input_schemas) > 0
            assert contract.output_schema is not None
            assert len(contract.required_edge_cases) > 0
            assert len(contract.required_adversarial_cases) > 0

    def test_registry_rejects_malformed_contracts(self):
        reg = CanonicalWorkloadRegistry()
        with pytest.raises(ValueError, match="Contract must have a non-empty stable string workload_id"):
            contract = CanonicalWorkloadContract(
                workload_id="",
                name="Empty ID",
                version="1.0.0",
                mathematical_contract="None",
                reference_impl_id="ref",
                candidate_impl_id="cand",
                exactness_class=ExactnessClass.BIT_EXACT,
                required_edge_cases=["edge"],
                required_adversarial_cases=["adv"],
            )
            reg.register(contract)

        with pytest.raises(ValueError, match="must specify mandatory edge cases"):
            contract = CanonicalWorkloadContract(
                workload_id="TEST_NO_EDGE",
                name="No Edge",
                version="1.0.0",
                mathematical_contract="None",
                reference_impl_id="ref",
                candidate_impl_id="cand",
                exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
                required_edge_cases=[],
                required_adversarial_cases=["adv"],
            )
            reg.register(contract)


class TestPhase2IndependentReference:
    """Verifies that reference implementations are mathematically sound and fail-closed."""

    def test_all_15_workloads_have_explicit_reference_handlers(self):
        for w_id in CANONICAL_15_WORKLOAD_IDS:
            inputs = StrictVerificationRunner.generate_typical_inputs(w_id, seed=123)
            ref_out, rec = IndependentReferenceEngine.execute_reference(w_id, inputs)
            assert ref_out is not None
            assert rec.is_independent is True
            assert rec.workload_id == w_id

    def test_unsupported_workload_raises_explicit_error(self):
        with pytest.raises(UnsupportedWorkloadError):
            IndependentReferenceEngine.execute_reference("NON_EXISTENT_WORKLOAD_XYZ", {"A": np.ones((2, 2))})

    def test_reference_cannot_be_fooled_by_generic_matrix_operands(self):
        # Workloads like ML_MLP_INFERENCE must not be swallowed by generic matmul
        inputs = {
            "X": np.ones((16, 64), dtype=np.float32),
            "W1": np.ones((64, 128), dtype=np.float32) * 0.01,
            "b1": np.zeros((128,), dtype=np.float32),
            "W2": np.ones((128, 32), dtype=np.float32) * 0.01,
            "b2": np.zeros((32,), dtype=np.float32),
        }
        ref_out, rec = IndependentReferenceEngine.execute_reference("ML_MLP_INFERENCE", inputs)
        assert rec.is_independent is True
        assert rec.output_shape == (16, 32)
        assert ref_out.shape == (16, 32)

    def test_streaming_vector_reference_implements_axpy(self):
        inputs = {
            "alpha": np.float32(2.5),
            "x": np.array([1.0, 2.0, 3.0], dtype=np.float32),
            "y": np.array([4.0, 5.0, 6.0], dtype=np.float32),
        }
        ref_out, rec = IndependentReferenceEngine.execute_reference("STREAMING_VECTOR_OPS", inputs)
        assert rec.is_independent is True
        expected = 2.5 * inputs["x"] + inputs["y"]
        np.testing.assert_allclose(ref_out, expected)


class TestPhase3CandidateCompiler:
    """Verifies that the candidate compiler compiles and executes correct algorithms."""

    def test_candidate_compiles_and_executes_gemm(self):
        inputs = StrictVerificationRunner.generate_typical_inputs("GEMM_STANDARD", seed=77)
        res, rec = CandidateCompiler.execute_candidate("GEMM_STANDARD", inputs)
        assert rec.is_success is True
        expected = inputs["A"] @ inputs["B"]
        np.testing.assert_allclose(res, expected, atol=1e-4, rtol=1e-4)

    def test_candidate_preserves_error_trace_on_invalid_inputs(self):
        # Incompatible inner dimensions
        inputs = {
            "A": np.ones((2, 3), dtype=np.float32),
            "B": np.ones((4, 2), dtype=np.float32),
        }
        res, rec = CandidateCompiler.execute_candidate("GEMM_STANDARD", inputs)
        assert rec.is_success is False
        assert rec.error_trace is not None


class TestPhase5VerifiedCache:
    """Verifies correctness-preserving multi-operand cache behavior."""

    def test_cache_hits_for_identical_inputs(self):
        cache = VerifiedExactCache(max_entries=10)
        inputs = {
            "A": np.array([[1.0, 2.0]], dtype=np.float32),
            "B": np.array([[3.0], [4.0]], dtype=np.float32),
        }
        outputs = np.array([[11.0]], dtype=np.float32)

        key = cache.compute_cache_key("GEMM_STANDARD", inputs)
        cache.put(key, "GEMM_STANDARD", outputs, is_verified=True)
        cached_res, hit, _ = cache.get(key)
        assert hit is True
        np.testing.assert_array_equal(cached_res, outputs)

    def test_cache_misses_if_operand_b_changes(self):
        cache = VerifiedExactCache(max_entries=10)
        inputs_1 = {
            "A": np.array([[1.0, 2.0]], dtype=np.float32),
            "B": np.array([[3.0], [4.0]], dtype=np.float32),
        }
        outputs = np.array([[11.0]], dtype=np.float32)
        key_1 = cache.compute_cache_key("GEMM_STANDARD", inputs_1)
        cache.put(key_1, "GEMM_STANDARD", outputs, is_verified=True)

        inputs_2 = {
            "A": np.array([[1.0, 2.0]], dtype=np.float32),
            "B": np.array([[3.0], [5.0]], dtype=np.float32),  # Changed operand B
        }
        key_2 = cache.compute_cache_key("GEMM_STANDARD", inputs_2)
        assert key_1 != key_2

        cached_res, hit, _ = cache.get(key_2)
        assert hit is False
        assert cached_res is None

    def test_cache_refuses_to_store_unverified_outputs(self):
        cache = VerifiedExactCache(max_entries=10)
        inputs = {"A": np.ones((2, 2), dtype=np.float32)}
        outputs = np.ones((2, 2), dtype=np.float32)
        key = cache.compute_cache_key("DUMMY_WORKLOAD", inputs)

        stored = cache.put(key, "DUMMY_WORKLOAD", outputs, is_verified=False)
        assert stored is False
        cached_res, hit, _ = cache.get(key)
        assert hit is False


class TestPhase6HardwareAttribution:
    """Verifies truthful hardware backend identification and absence of deceptive claims."""

    def test_hardware_backend_detects_real_system_attributes(self):
        backend_mgr = HardwareBackendManager()
        profile = backend_mgr.profile
        assert profile.physical_cores > 0
        assert profile.logical_processors >= profile.physical_cores
        assert profile.ram_total_gb > 0
        # Must not fabricate an NVIDIA RTX discrete GPU
        assert profile.discrete_gpu_detected is False
        assert profile.discrete_gpu_model is None
        # Verification of detected iGPU
        if profile.igpu_detected:
            assert "Intel" in (profile.igpu_model or "")

    def test_hardware_backend_records_actual_execution(self):
        backend_mgr = HardwareBackendManager()
        def dummy_cand(inputs):
            return inputs["A"] @ inputs["B"], ["dummy_matmul"]

        inputs = {
            "A": np.eye(4, dtype=np.float32),
            "B": np.eye(4, dtype=np.float32),
        }
        res, actual_backend, latency_ms, fallback, _ = backend_mgr.execute_workload(
            "GEMM_STANDARD", inputs, dummy_cand, prefer_igpu=False
        )
        assert actual_backend in ["CPU_AVX2", "FALLBACK_CPU", "INTEL_UHD_IGPU (OpenVINO)"]
        assert latency_ms >= 0.0
        np.testing.assert_allclose(res, np.eye(4, dtype=np.float32))


class TestPhase7And8VerificationStateMachine:
    """Verifies adversarial battery, fail-closed verification, and faulty-candidate rejection."""

    def test_all_15_canonical_workloads_pass_strict_verification(self):
        report = StrictVerificationRunner.verify_all_canonical_workloads(seed=42)
        assert report.total_workloads == 15
        assert report.pass_count == 15
        assert report.fail_count == 0
        assert report.blocked_count == 0
        assert report.is_15_of_15_verified is True

    def test_faulty_candidate_is_rejected_and_flagged_fail(self):
        # Verify single workload compliance check rejection with corrupted output
        contract = CANONICAL_REGISTRY.get("GEMM_STANDARD")
        inputs = StrictVerificationRunner.generate_typical_inputs("GEMM_STANDARD", seed=42)
        ref_out, _ = IndependentReferenceEngine.execute_reference("GEMM_STANDARD", inputs)
        corrupted_cand = ref_out + 1.0  # Deliberate corruption
        passed, status, _ = contract.check_output_compliance(corrupted_cand, ref_out)
        assert passed is False
        assert "FAIL" in status

    def test_non_contiguous_array_handled_cleanly(self):
        # Verify that non-contiguous slices are correctly compared
        a_full = np.arange(256 * 128, dtype=np.float32).reshape(256, 128)
        a = a_full[::2, :]  # shape (128, 128), non-contiguous
        b = np.ones((128, 128), dtype=np.float32)
        inputs = {"A": a, "B": b}
        ref_out, _ = IndependentReferenceEngine.execute_reference("GEMM_STANDARD", inputs)
        cand_out, _ = CandidateCompiler.execute_candidate("GEMM_STANDARD", inputs)
        contract = CANONICAL_REGISTRY.get("GEMM_STANDARD")
        passed, msg, _ = contract.check_output_compliance(cand_out, ref_out)
        assert passed is True


class TestPhase11FastAPIRouter:
    """Verifies that the canonical workload REST API endpoints function correctly."""

    def test_get_status_endpoint(self):
        response = client.get("/api/v1/workloads/canonical/status")
        assert response.status_code == 200
        data = response.json()
        assert data["total_canonical_workloads"] == 15
        assert "host_hardware" in data
        assert data["status"] == "OPERATIONAL"

    def test_get_registry_endpoint(self):
        response = client.get("/api/v1/workloads/canonical/registry")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 15
        w_ids = [item["workload_id"] for item in data]
        assert "GEMM_STANDARD" in w_ids

    def test_get_individual_workload_contract(self):
        response = client.get("/api/v1/workloads/canonical/workload/GEMM_STANDARD")
        assert response.status_code == 200
        data = response.json()
        assert data["workload_id"] == "GEMM_STANDARD"
        assert data["exactness_class"] == "NUMERICALLY_EQUIVALENT"

    def test_verify_endpoint_runs_and_reports_15_15(self):
        response = client.post("/api/v1/workloads/canonical/verify", json={"seed": 42})
        assert response.status_code == 200
        data = response.json()
        assert data["total_workloads"] == 15
        assert data["pass_count"] == 15
        assert data["is_15_of_15_verified"] is True
        assert data["fail_count"] == 0
