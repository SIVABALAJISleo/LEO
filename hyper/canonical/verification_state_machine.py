"""
hyper/canonical/verification_state_machine.py
=============================================
Authoritative Strict Verification State Machine and Adversarial Suite Runner.

Implements the formal 5-State Verification Machine:
- PASS: Contract defined, independent candidate and reference executed,
        primary and adversarial cases passed, backend truthfully reported.
- FAIL: Output property mismatch, numerical tolerance exceeded, or adversarial violation.
- UNKNOWN: Missing reference, unverified condition, or ambiguous status.
- BLOCKED: Resource exhaustion, missing dependency, or unexpected crash.
- NOT_RUN: Workload defined but not yet evaluated.

AGGREGATION RULE:
15/15 is permitted ONLY if all 15 workloads independently achieve verified PASS status.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
import math
import sys
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper.canonical.workload_registry import (
    CanonicalWorkloadContract,
    ExactnessClass,
    CANONICAL_REGISTRY,
)
from hyper.canonical.independent_reference import (
    IndependentReferenceEngine,
    UnsupportedWorkloadError,
)
from hyper.canonical.candidate_compiler import CandidateCompiler
from hyper.canonical.hardware_backends import HARDWARE_BACKEND
from hyper.canonical.verified_cache import VERIFIED_CACHE


class VerificationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    NOT_RUN = "NOT_RUN"
    UNSUPPORTED = "UNSUPPORTED"
    BLOCKED = "BLOCKED"


@dataclasses.dataclass
class WorkloadVerificationRecord:
    """Individual workload verification evidence."""
    workload_id: str
    status: VerificationStatus
    exactness_class: str
    reference_impl_id: str
    candidate_impl_id: str
    primary_passed: bool
    adversarial_passed: bool
    adversarial_cases_tested: int
    adversarial_cases_passed: int
    backend_used: str
    candidate_latency_ms: float
    reference_latency_ms: float
    speedup: float
    failure_reasons: List[str]
    reproducibility_seed: int
    timestamp: float = dataclasses.field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "status": self.status.value,
            "exactness_class": self.exactness_class,
            "reference_impl_id": self.reference_impl_id,
            "candidate_impl_id": self.candidate_impl_id,
            "primary_passed": self.primary_passed,
            "adversarial_passed": self.adversarial_passed,
            "adversarial_cases_tested": self.adversarial_cases_tested,
            "adversarial_cases_passed": self.adversarial_cases_passed,
            "backend_used": self.backend_used,
            "candidate_latency_ms": round(self.candidate_latency_ms, 4),
            "reference_latency_ms": round(self.reference_latency_ms, 4),
            "speedup": round(self.speedup, 2),
            "failure_reasons": self.failure_reasons,
            "reproducibility_seed": self.reproducibility_seed,
            "timestamp": self.timestamp,
        }


@dataclasses.dataclass
class SuiteVerificationReport:
    """Consolidated report across all 15 workloads."""
    total_workloads: int
    pass_count: int
    fail_count: int
    unknown_count: int
    unsupported_count: int
    blocked_count: int
    not_run_count: int
    is_15_of_15_verified: bool
    status_summary: str
    records: Dict[str, WorkloadVerificationRecord]
    hardware_profile: Dict[str, Any]
    environment: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_workloads": self.total_workloads,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "unknown_count": self.unknown_count,
            "unsupported_count": self.unsupported_count,
            "blocked_count": self.blocked_count,
            "not_run_count": self.not_run_count,
            "is_15_of_15_verified": self.is_15_of_15_verified,
            "status_summary": self.status_summary,
            "records": {k: v.to_dict() for k, v in self.records.items()},
            "hardware_profile": self.hardware_profile,
            "environment": self.environment,
        }


class StrictVerificationRunner:
    """
    Executes the formal verification battery across all canonical workloads.
    """

    @classmethod
    def generate_typical_inputs(cls, workload_id: str, seed: int = 42) -> Dict[str, Any]:
        """Generates deterministic, typical input tensors using a fixed seed."""
        rng = np.random.default_rng(seed)

        if workload_id == "GEMM_STANDARD":
            return {
                "A": rng.standard_normal((128, 128)).astype(np.float32),
                "B": rng.standard_normal((128, 128)).astype(np.float32),
            }
        elif workload_id == "CONV2D_STANDARD":
            return {
                "image": rng.standard_normal((64, 64)).astype(np.float32),
                "kernel": rng.standard_normal((5, 5)).astype(np.float32),
            }
        elif workload_id == "FFT_STANDARD":
            sig = rng.standard_normal(1024) + 1j * rng.standard_normal(1024)
            return {"x": sig.astype(np.complex64)}
        elif workload_id == "REDUCTION_SUM":
            return {"x": rng.standard_normal(100000).astype(np.float32)}
        elif workload_id == "SORT_STANDARD":
            return {"x": rng.standard_normal(10000).astype(np.float32)}
        elif workload_id == "PAGERANK_GRAPH":
            raw = rng.random((128, 128)).astype(np.float32)
            adj = (raw > 0.85).astype(np.float32)
            return {"adj_matrix": adj}
        elif workload_id == "SHA256_CRYPTO":
            return {"data": b"LEO_HYPER_CANONICAL_VERIFICATION_PAYLOAD_BLOCK_1024_" * 64}
        elif workload_id == "NBODY_GRAVITATIONAL":
            return {
                "positions": rng.standard_normal((256, 3)).astype(np.float32),
                "velocities": rng.standard_normal((256, 3)).astype(np.float32) * 0.1,
                "masses": rng.uniform(1.0, 10.0, size=(256,)).astype(np.float32),
                "dt": 0.01,
            }
        elif workload_id == "ML_MLP_INFERENCE":
            return {
                "X": rng.standard_normal((64, 128)).astype(np.float32),
                "W1": rng.standard_normal((128, 64)).astype(np.float32) * 0.1,
                "b1": rng.standard_normal((64,)).astype(np.float32) * 0.01,
                "W2": rng.standard_normal((64, 64)).astype(np.float32) * 0.1,
                "b2": rng.standard_normal((64,)).astype(np.float32) * 0.01,
            }
        elif workload_id == "ATTENTION_HEAD":
            return {
                "Q": rng.standard_normal((1, 32, 64)).astype(np.float32),
                "K": rng.standard_normal((1, 32, 64)).astype(np.float32),
                "V": rng.standard_normal((1, 32, 64)).astype(np.float32),
            }
        elif workload_id == "SOBEL_FILTER":
            return {"image": rng.standard_normal((128, 128)).astype(np.float32)}
        elif workload_id == "STREAMING_VECTOR_OPS":
            return {
                "x": rng.standard_normal(1000000).astype(np.float32),
                "y": rng.standard_normal(1000000).astype(np.float32),
                "alpha": 2.5,
            }
        elif workload_id == "MANDELBROT_FRACTAL":
            x = np.linspace(-2.0, 1.0, 128, dtype=np.float32)
            y = np.linspace(-1.5, 1.5, 128, dtype=np.float32)
            xx, yy = np.meshgrid(x, y)
            return {"c_grid": (xx + 1j * yy).astype(np.complex64)}
        elif workload_id == "SPMV_IRREGULAR_CSR":
            N = 128
            nnz = 2048
            indptr = np.sort(rng.integers(0, nnz, size=N + 1, dtype=np.int32))
            indptr[0] = 0
            indptr[-1] = nnz
            indices = rng.integers(0, N, size=nnz, dtype=np.int32)
            data = rng.standard_normal(nnz).astype(np.float32)
            x = rng.standard_normal(N).astype(np.float32)
            return {"data": data, "indices": indices, "indptr": indptr, "x": x}
        elif workload_id == "ADVERSARIAL_HILBERT_STRESS":
            dim = 32
            i_idx = np.arange(1, dim + 1)[:, None]
            j_idx = np.arange(1, dim + 1)[None, :]
            H = (1.0 / (i_idx + j_idx - 1.0)).astype(np.float32)
            B = rng.standard_normal((dim, dim)).astype(np.float32)
            return {"A": H, "B": B}
        else:
            raise UnsupportedWorkloadError(f"Unknown typical input generator for '{workload_id}'")

    @classmethod
    def generate_adversarial_cases(cls, workload_id: str, seed: int = 101) -> List[Tuple[str, Dict[str, Any]]]:
        """Generates a battery of boundary and stress-testing input configurations."""
        rng = np.random.default_rng(seed)
        cases: List[Tuple[str, Dict[str, Any]]] = []

        if workload_id == "GEMM_STANDARD":
            # 1. Identity B
            cases.append(("identity_B", {
                "A": rng.standard_normal((128, 128)).astype(np.float32),
                "B": np.eye(128, dtype=np.float32),
            }))
            # 2. Zero B
            cases.append(("zero_B", {
                "A": rng.standard_normal((128, 128)).astype(np.float32),
                "B": np.zeros((128, 128), dtype=np.float32),
            }))
            # 3. Non-contiguous input
            A_full = rng.standard_normal((256, 128)).astype(np.float32)
            B_full = rng.standard_normal((128, 256)).astype(np.float32)
            cases.append(("non_contiguous_slices", {
                "A": A_full[::2, :],
                "B": B_full[:, ::2],
            }))

        elif workload_id == "CONV2D_STANDARD":
            cases.append(("zero_kernel", {
                "image": rng.standard_normal((64, 64)).astype(np.float32),
                "kernel": np.zeros((5, 5), dtype=np.float32),
            }))
            impulse = np.zeros((5, 5), dtype=np.float32)
            impulse[2, 2] = 1.0
            cases.append(("delta_impulse_kernel", {
                "image": rng.standard_normal((64, 64)).astype(np.float32),
                "kernel": impulse,
            }))

        elif workload_id == "FFT_STANDARD":
            cases.append(("dc_constant", {
                "x": np.ones(1024, dtype=np.complex64),
            }))
            cases.append(("pure_imaginary_chirp", {
                "x": (1j * np.sin(np.linspace(0, 50, 1024))).astype(np.complex64),
            }))

        elif workload_id == "REDUCTION_SUM":
            cases.append(("all_zeros", {"x": np.zeros(100000, dtype=np.float32)}))
            cases.append(("alternating_canceling_ones", {
                "x": np.tile(np.array([1.0, -1.0], dtype=np.float32), 50000),
            }))
            # Swamping: large number + 1e-4
            swamp = np.zeros(100000, dtype=np.float32)
            swamp[0] = 1e6
            swamp[1:] = 1e-3
            cases.append(("swamping_dynamic_range", {"x": swamp}))

        elif workload_id == "SORT_STANDARD":
            cases.append(("already_sorted", {"x": np.arange(10000, dtype=np.float32)}))
            cases.append(("reverse_sorted", {"x": np.arange(10000, 0, -1, dtype=np.float32)}))
            cases.append(("all_identical_elements", {"x": np.ones(10000, dtype=np.float32) * 42.0}))

        elif workload_id == "PAGERANK_GRAPH":
            cases.append(("empty_zero_matrix", {"adj_matrix": np.zeros((128, 128), dtype=np.float32)}))
            cases.append(("uniform_complete_mesh", {"adj_matrix": np.ones((128, 128), dtype=np.float32)}))

        elif workload_id == "SHA256_CRYPTO":
            cases.append(("empty_bytes", {"data": b""}))
            cases.append(("exact_55_byte_block", {"data": b"A" * 55}))
            cases.append(("exact_64_byte_block", {"data": b"B" * 64}))

        elif workload_id == "NBODY_GRAVITATIONAL":
            cases.append(("zero_velocities", {
                "positions": rng.standard_normal((256, 3)).astype(np.float32),
                "velocities": np.zeros((256, 3), dtype=np.float32),
                "masses": np.ones(256, dtype=np.float32),
                "dt": 0.01,
            }))

        elif workload_id == "ML_MLP_INFERENCE":
            cases.append(("all_negative_preactivation", {
                "X": -np.ones((64, 128), dtype=np.float32),
                "W1": np.ones((128, 64), dtype=np.float32) * 0.1,
                "b1": -np.ones((64,), dtype=np.float32) * 100.0,
                "W2": np.ones((64, 64), dtype=np.float32) * 0.1,
                "b2": np.zeros((64,), dtype=np.float32),
            }))

        elif workload_id == "ATTENTION_HEAD":
            cases.append(("all_zero_query", {
                "Q": np.zeros((1, 32, 64), dtype=np.float32),
                "K": rng.standard_normal((1, 32, 64)).astype(np.float32),
                "V": rng.standard_normal((1, 32, 64)).astype(np.float32),
            }))

        elif workload_id == "SOBEL_FILTER":
            cases.append(("flat_constant_image", {"image": np.ones((128, 128), dtype=np.float32) * 100.0}))

        elif workload_id == "STREAMING_VECTOR_OPS":
            cases.append(("alpha_is_zero", {
                "x": rng.standard_normal(1000000).astype(np.float32),
                "y": rng.standard_normal(1000000).astype(np.float32),
                "alpha": 0.0,
            }))
            cases.append(("alpha_is_one", {
                "x": rng.standard_normal(1000000).astype(np.float32),
                "y": rng.standard_normal(1000000).astype(np.float32),
                "alpha": 1.0,
            }))

        elif workload_id == "MANDELBROT_FRACTAL":
            # Grid of pure origin points
            cases.append(("pure_origin_grid", {"c_grid": np.zeros((128, 128), dtype=np.complex64)}))
            # Grid of clearly escaped points (|c| = 10)
            cases.append(("clearly_escaped_grid", {"c_grid": (np.ones((128, 128)) * 10.0).astype(np.complex64)}))

        elif workload_id == "SPMV_IRREGULAR_CSR":
            cases.append(("empty_matrix_all_zeros", {
                "data": np.zeros(2048, dtype=np.float32),
                "indices": np.zeros(2048, dtype=np.int32),
                "indptr": np.zeros(129, dtype=np.int32),
                "x": rng.standard_normal(128).astype(np.float32),
            }))

        elif workload_id == "ADVERSARIAL_HILBERT_STRESS":
            dim = 32
            H = (1.0 / (np.arange(1, dim + 1)[:, None] + np.arange(1, dim + 1)[None, :] - 1.0)).astype(np.float32)
            cases.append(("identity_B", {"A": H, "B": np.eye(dim, dtype=np.float32)}))
            cases.append(("zero_B", {"A": H, "B": np.zeros((dim, dim), dtype=np.float32)}))

        return cases

    @classmethod
    def verify_workload(
        cls,
        workload_id: str,
        seed: int = 42,
        prefer_igpu: bool = True,
    ) -> WorkloadVerificationRecord:
        """
        Runs comprehensive verification on a single canonical workload.
        """
        contract = CANONICAL_REGISTRY.get(workload_id)
        if contract is None:
            return WorkloadVerificationRecord(
                workload_id=workload_id,
                status=VerificationStatus.UNSUPPORTED,
                exactness_class="UNKNOWN",
                reference_impl_id="NONE",
                candidate_impl_id="NONE",
                primary_passed=False,
                adversarial_passed=False,
                adversarial_cases_tested=0,
                adversarial_cases_passed=0,
                backend_used="NONE",
                candidate_latency_ms=0.0,
                reference_latency_ms=0.0,
                speedup=0.0,
                failure_reasons=[f"Workload '{workload_id}' not found in canonical registry"],
                reproducibility_seed=seed,
            )

        failures: List[str] = []

        # ---------------------------------------------------------------------
        # 1. Primary Typical Input Verification
        # ---------------------------------------------------------------------
        try:
            typical_inputs = cls.generate_typical_inputs(workload_id, seed=seed)
        except Exception as e:
            return WorkloadVerificationRecord(
                workload_id=workload_id,
                status=VerificationStatus.BLOCKED,
                exactness_class=contract.exactness_class.value,
                reference_impl_id=contract.reference_impl_id,
                candidate_impl_id=contract.candidate_impl_id,
                primary_passed=False,
                adversarial_passed=False,
                adversarial_cases_tested=0,
                adversarial_cases_passed=0,
                backend_used="NONE",
                candidate_latency_ms=0.0,
                reference_latency_ms=0.0,
                speedup=0.0,
                failure_reasons=[f"Failed to generate typical inputs: {e}"],
                reproducibility_seed=seed,
            )

        # Independent Reference Execution
        try:
            ref_output, ref_record = IndependentReferenceEngine.execute_reference(workload_id, typical_inputs)
        except Exception as e:
            return WorkloadVerificationRecord(
                workload_id=workload_id,
                status=VerificationStatus.BLOCKED,
                exactness_class=contract.exactness_class.value,
                reference_impl_id=contract.reference_impl_id,
                candidate_impl_id=contract.candidate_impl_id,
                primary_passed=False,
                adversarial_passed=False,
                adversarial_cases_tested=0,
                adversarial_cases_passed=0,
                backend_used="NONE",
                candidate_latency_ms=0.0,
                reference_latency_ms=0.0,
                speedup=0.0,
                failure_reasons=[f"Reference execution failed: {e}"],
                reproducibility_seed=seed,
            )

        # Candidate Execution (with hardware selection)
        cand_output, cand_record = CandidateCompiler.execute_candidate(
            workload_id=workload_id,
            inputs=typical_inputs,
            contract=contract,
            target_backend="INTEL_UHD_IGPU" if (prefer_igpu and workload_id == "GEMM_STANDARD") else "CPU_AVX2",
        )

        if not cand_record.is_success:
            return WorkloadVerificationRecord(
                workload_id=workload_id,
                status=VerificationStatus.FAIL,
                exactness_class=contract.exactness_class.value,
                reference_impl_id=contract.reference_impl_id,
                candidate_impl_id=contract.candidate_impl_id,
                primary_passed=False,
                adversarial_passed=False,
                adversarial_cases_tested=0,
                adversarial_cases_passed=0,
                backend_used=cand_record.selected_backend,
                candidate_latency_ms=cand_record.execution_time_ms,
                reference_latency_ms=ref_record.execution_time_ms,
                speedup=0.0,
                failure_reasons=[f"Candidate crashed: {cand_record.error_trace}"],
                reproducibility_seed=seed,
            )

        # Primary Contract Compliance Check
        primary_ok, primary_status, primary_metrics = contract.check_output_compliance(cand_output, ref_output)
        if not primary_ok:
            failures.append(f"Primary output mismatch: {primary_status}")

        # ---------------------------------------------------------------------
        # 2. Adversarial Battery Verification
        # ---------------------------------------------------------------------
        adv_cases = cls.generate_adversarial_cases(workload_id, seed=seed + 100)
        adv_tested = len(adv_cases)
        adv_passed_count = 0

        for case_name, adv_inputs in adv_cases:
            try:
                adv_ref, _ = IndependentReferenceEngine.execute_reference(workload_id, adv_inputs)
                adv_cand, adv_cand_rec = CandidateCompiler.execute_candidate(workload_id, adv_inputs, contract=contract)
                if not adv_cand_rec.is_success:
                    failures.append(f"Adversarial case '{case_name}' candidate failed: {adv_cand_rec.error_trace}")
                    continue
                c_ok, c_stat, _ = contract.check_output_compliance(adv_cand, adv_ref)
                if c_ok:
                    adv_passed_count += 1
                else:
                    failures.append(f"Adversarial case '{case_name}' mismatch: {c_stat}")
            except Exception as e:
                failures.append(f"Adversarial case '{case_name}' threw exception: {e}")

        adversarial_ok = (adv_passed_count == adv_tested) and adv_tested > 0

        # Calculate speedup
        cand_time = max(0.0001, cand_record.execution_time_ms)
        ref_time = ref_record.execution_time_ms
        speedup = ref_time / cand_time

        # Final State Machine Evaluation
        if primary_ok and adversarial_ok and len(failures) == 0:
            final_status = VerificationStatus.PASS
            # Cache the verified output
            cache_key = VERIFIED_CACHE.compute_cache_key(workload_id, typical_inputs, contract.version)
            VERIFIED_CACHE.put(cache_key, workload_id, cand_output, contract.version, is_verified=True)
        else:
            final_status = VerificationStatus.FAIL

        return WorkloadVerificationRecord(
            workload_id=workload_id,
            status=final_status,
            exactness_class=contract.exactness_class.value,
            reference_impl_id=contract.reference_impl_id,
            candidate_impl_id=contract.candidate_impl_id,
            primary_passed=primary_ok,
            adversarial_passed=adversarial_ok,
            adversarial_cases_tested=adv_tested,
            adversarial_cases_passed=adv_passed_count,
            backend_used=cand_record.selected_backend,
            candidate_latency_ms=cand_record.execution_time_ms,
            reference_latency_ms=ref_record.execution_time_ms,
            speedup=speedup,
            failure_reasons=failures,
            reproducibility_seed=seed,
        )

    @classmethod
    def verify_all_canonical_workloads(
        cls,
        seed: int = 42,
        prefer_igpu: bool = True,
    ) -> SuiteVerificationReport:
        """
        Executes full canonical verification across all 15 workloads.
        """
        all_ids = CANONICAL_REGISTRY.list_workloads()
        records: Dict[str, WorkloadVerificationRecord] = {}

        pass_c = 0
        fail_c = 0
        unknown_c = 0
        unsupported_c = 0
        blocked_c = 0
        not_run_c = 0

        for wid in all_ids:
            rec = cls.verify_workload(wid, seed=seed, prefer_igpu=prefer_igpu)
            records[wid] = rec
            if rec.status == VerificationStatus.PASS:
                pass_c += 1
            elif rec.status == VerificationStatus.FAIL:
                fail_c += 1
            elif rec.status == VerificationStatus.UNKNOWN:
                unknown_c += 1
            elif rec.status == VerificationStatus.UNSUPPORTED:
                unsupported_c += 1
            elif rec.status == VerificationStatus.BLOCKED:
                blocked_c += 1
            elif rec.status == VerificationStatus.NOT_RUN:
                not_run_c += 1

        total = len(all_ids)
        is_15_verified = (
            (pass_c == total)
            and (total == 15)
            and (fail_c == 0)
            and (unknown_c == 0)
            and (unsupported_c == 0)
            and (blocked_c == 0)
            and (not_run_c == 0)
        )

        summary = (
            f"15/15 CANONICAL WORKLOAD CONTRACTS VERIFIED (PASS: {pass_c}/{total})"
            if is_15_verified
            else f"VERIFICATION FAILED: {pass_c}/{total} PASS (FAIL: {fail_c}, UNKNOWN: {unknown_c}, UNSUPPORTED: {unsupported_c}, BLOCKED: {blocked_c})"
        )

        return SuiteVerificationReport(
            total_workloads=total,
            pass_count=pass_c,
            fail_count=fail_c,
            unknown_count=unknown_c,
            unsupported_count=unsupported_c,
            blocked_count=blocked_c,
            not_run_count=not_run_c,
            is_15_of_15_verified=is_15_verified,
            status_summary=summary,
            records=records,
            hardware_profile=HARDWARE_BACKEND.profile.to_dict(),
            environment={
                "platform": sys.platform,
                "python_version": sys.version,
                "numpy_version": np.__version__,
                "timestamp": time.time(),
            },
        )
