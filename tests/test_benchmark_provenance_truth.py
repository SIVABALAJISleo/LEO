"""
tests/test_benchmark_provenance_truth.py
========================================
Regression and integrity test suite ensuring:
1. No simulated GPU benchmarks are presented as real hardware measurements.
2. All metrics identify explicit provenance (MEASURED, SIMULATED_REFERENCE, UNKNOWN).
3. Operation count and work elimination are substantiated by algorithm models, never inferred from latency ratios.
4. Fail-closed gates prevent certification bypass when adversarial or holdout checks fail.
5. Memory copying via ctypes.memmove is truthfully reported and never labeled zero-copy.
6. CPU fallback in heterogeneous orchestrators is truthfully labeled CPU_ONLY_FALLBACK.
"""

import pytest
import numpy as np

from hyper_x.omega_runner import HyperOmegaRunner, OmegaRunConfig
from hyper_x.reference_engine import ExternalReferenceEngine, ExternalReferenceManifest
from hyper_x.equivalence_verifier import EquivalenceMode, VerificationVerdict
from hyper_x.certificates.work_certificate import ExternalEquivalenceWorkCertificate
from hyper_x.heterogeneous_orchestrator import HeterogeneousOrchestrator
from hyper.extreme.opencl_uva import OpenCLZeroCopyUVA


def test_reference_engine_provenance_and_no_fake_hardware():
    """Verify reference engine marks provenance truthfully and avoids fake hardware claims."""
    engine = ExternalReferenceEngine()
    dummy_in = np.ones((16, 16), dtype=np.float32)
    dummy_out = np.ones((16, 16), dtype=np.float32)

    # 1. Measured local host baseline
    manifest_local = engine.register_reference(
        workload_id="TEST_LOCAL_001",
        input_data=dummy_in,
        output_data=dummy_out,
        reference_latency_ms=1.25,
        nominal_operations=2.0 * (16 ** 3),
        nominal_memory_bytes=1024,
        provenance="MEASURED",
    )
    assert manifest_local.provenance == "MEASURED"
    assert manifest_local.is_simulated is False
    assert "RTX 5090" not in manifest_local.gpu_identity
    assert "Host Baseline" in manifest_local.gpu_identity

    # 2. Simulated reference target
    manifest_sim = engine.register_reference(
        workload_id="TEST_SIM_001",
        input_data=dummy_in,
        output_data=dummy_out,
        reference_latency_ms=0.08,
        nominal_operations=2.0 * (16 ** 3),
        nominal_memory_bytes=1024,
        provenance="SIMULATED_REFERENCE",
    )
    assert manifest_sim.provenance == "SIMULATED_REFERENCE"
    assert manifest_sim.is_simulated is True
    assert "SIMULATED_TARGET" in manifest_sim.gpu_identity


def test_omega_runner_no_latency_ratio_work_elimination():
    """Verify that omega_runner never computes work elimination from latency ratio."""
    runner = HyperOmegaRunner()
    N = 64
    nominal_ops = 2.0 * (N ** 3)
    nominal_bytes = float(3 * N * N * 4)

    rng = np.random.RandomState(42)
    A = rng.randn(N, N).astype(np.float32)
    B = rng.randn(N, N).astype(np.float32)

    config = OmegaRunConfig(
        workload_id="TEST_PROVENANCE_GEMM",
        equivalence_mode=EquivalenceMode.NUMERICALLY_EQUIVALENT,
        adversarial_samples=1,
        holdout_samples=1,
    )

    # Candidate has nominal operations (no algorithmic work elimination)
    res = runner.run_workload(
        config=config,
        canonical_input=(A, B),
        reference_fn=lambda inp: np.matmul(inp[0], inp[1]),
        candidate_fn=lambda inp: np.dot(inp[0], inp[1]),
        adversarial_generator=lambda s: (np.eye(N, dtype=np.float32), np.eye(N, dtype=np.float32)),
        holdout_generator=lambda s: (np.zeros((N, N), dtype=np.float32), np.zeros((N, N), dtype=np.float32)),
        nominal_operations=nominal_ops,
        nominal_memory_bytes=nominal_bytes,
        candidate_operations=nominal_ops,
    )

    cert = res.certificate
    # Under honest accounting, standard GEMM does not eliminate operations
    assert cert.candidate_operation_count == nominal_ops
    assert cert.verified_work_elimination == 0.0
    assert cert.reference_provenance == "MEASURED"
    assert cert.candidate_provenance == "MEASURED"
    assert cert.measured_reference_latency_ms > 0
    assert cert.candidate_latency_ms > 0
    assert cert.candidate_memory_bytes > 0


def test_omega_runner_fail_closed_on_adversarial_failure():
    """Verify that adversarial test failure blocks certification and returns FAILED status."""
    runner = HyperOmegaRunner()
    N = 32
    nominal_ops = 2.0 * (N ** 3)

    A = np.ones((N, N), dtype=np.float32)
    B = np.ones((N, N), dtype=np.float32)

    config = OmegaRunConfig(
        workload_id="TEST_FAIL_CLOSED_ADV",
        equivalence_mode=EquivalenceMode.NUMERICALLY_EQUIVALENT,
        adversarial_samples=2,
    )

    # Candidate that passes canonical input but deliberately fails on adversarial inputs
    def buggy_candidate(inputs):
        a, b = inputs
        if np.allclose(a, 1.0):
            return np.matmul(a, b)
        # Corrupt output on adversarial cases
        return np.zeros_like(a)

    def hostile_generator(seed: int):
        return np.full((N, N), float(seed), dtype=np.float32), np.eye(N, dtype=np.float32)

    res = runner.run_workload(
        config=config,
        canonical_input=(A, B),
        reference_fn=lambda inp: np.matmul(inp[0], inp[1]),
        candidate_fn=buggy_candidate,
        adversarial_generator=hostile_generator,
        nominal_operations=nominal_ops,
    )

    assert res.certificate.adversarial_result == "FAIL"
    # Status MUST be FAILED - never VERIFIED!
    assert res.status == "FAILED"
    assert res.certificate.status == "FAILED"


def test_omega_runner_fail_closed_on_holdout_failure():
    """Verify that holdout test failure blocks certification and returns FAILED status."""
    runner = HyperOmegaRunner()
    N = 32
    nominal_ops = 2.0 * (N ** 3)

    A = np.ones((N, N), dtype=np.float32)
    B = np.ones((N, N), dtype=np.float32)

    config = OmegaRunConfig(
        workload_id="TEST_FAIL_CLOSED_HOLDOUT",
        equivalence_mode=EquivalenceMode.NUMERICALLY_EQUIVALENT,
        adversarial_samples=1,
        holdout_samples=2,
    )

    def buggy_candidate(inputs):
        a, b = inputs
        if np.allclose(a, 1.0):
            return np.matmul(a, b)
        # Corrupt output on holdout cases
        return np.full_like(a, 999.0)

    res = runner.run_workload(
        config=config,
        canonical_input=(A, B),
        reference_fn=lambda inp: np.matmul(inp[0], inp[1]),
        candidate_fn=buggy_candidate,
        adversarial_generator=lambda s: (np.ones((N, N), dtype=np.float32), np.ones((N, N), dtype=np.float32)),
        holdout_generator=lambda s: (np.full((N, N), 5.0, dtype=np.float32), np.eye(N, dtype=np.float32)),
        nominal_operations=nominal_ops,
    )

    assert res.certificate.holdout_result == "FAIL"
    assert res.status == "FAILED"
    assert res.certificate.status == "FAILED"


def test_opencl_uva_truthful_copy_reporting():
    """Verify that OpenCL UVA memory methods report true copy overhead bytes and no false zero-copy."""
    uva = OpenCLZeroCopyUVA()
    A = np.ones((16, 16), dtype=np.float32)
    B = np.ones((16, 16), dtype=np.float32)

    _, meta = uva.execute_zero_copy_gemm(A, B)
    if meta.get("backend") == "INTEL_UHD_OPENCL_HOST_PINNED_MAPPED":
        # Must report actual bytes moved via ctypes.memmove
        assert meta["copy_overhead_bytes"] > 0
        assert meta["is_zero_copy"] is False
        assert meta["memory_mode"] == "HOST_PINNED_MAPPED_COPY"
    else:
        # Fallback path if OpenCL context is unavailable
        assert meta["is_zero_copy"] is False


def test_heterogeneous_orchestrator_truthful_fallback():
    """Verify orchestrator reports CPU_ONLY_FALLBACK truthfully when GPU is disabled or unavailable."""
    orch = HeterogeneousOrchestrator()
    # Force simulated fallback scenario
    orch.is_real_gpu = False

    A = np.ones((16, 16), dtype=np.float32)
    B = np.ones((16, 16), dtype=np.float32)

    C, meta = orch.execute_overlapped_pipeline(A, B)
    assert meta["execution_mode"] == "CPU_ONLY_FALLBACK"
    assert meta["is_real_gpu_executed"] is False
    assert np.allclose(C, A @ B)
