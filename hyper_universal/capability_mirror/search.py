"""
hyper_universal/capability_mirror/search.py
Capability Substitution Search Engine:
Evaluates requested GPU capabilities, identifies what the application actually observes,
searches for software and mathematical alternatives, estimates costs, independently verifies
outputs, measures end-to-end performance, and rates equivalence across 6 distinct dimensions.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np

from hyper_universal.capability_mirror.registry import (
    CapabilityRecord,
    CapabilityCertificationStatus,
    EquivalenceDimension,
    UniversalCapabilityRegistry,
)


@dataclass
class SubstitutionCandidate:
    capability_id: str
    substitution_type: str  # "CPU_AVX2", "INTEL_UHD_IGPU", "ALGORITHMIC_REPLACEMENT", "SOFTWARE_EMULATION"
    observable_behavior_match: bool
    requires_physical_hardware: bool
    estimated_flops: float
    estimated_memory_bytes: int
    measured_latency_ms: float
    measured_speedup_vs_reference: float
    is_correctness_verified: bool
    verification_error_relative: float
    verification_error_absolute: float
    certification_status: CapabilityCertificationStatus
    equivalence_ratings: Dict[str, bool]  # Dimension name -> Boolean
    limitations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "substitution_type": self.substitution_type,
            "observable_behavior_match": self.observable_behavior_match,
            "requires_physical_hardware": self.requires_physical_hardware,
            "estimated_flops": self.estimated_flops,
            "estimated_memory_bytes": self.estimated_memory_bytes,
            "measured_latency_ms": round(self.measured_latency_ms, 3),
            "measured_speedup": round(self.measured_speedup_vs_reference, 2),
            "is_correctness_verified": self.is_correctness_verified,
            "rel_error": self.verification_error_relative,
            "abs_error": self.verification_error_absolute,
            "certification_status": self.certification_status.value,
            "equivalence_ratings": self.equivalence_ratings,
            "limitations": self.limitations,
        }


class CapabilitySubstitutionSearch:
    """
    Evaluates requested GPU capabilities and searches for valid software alternatives.
    """

    def __init__(self, registry: Optional[UniversalCapabilityRegistry] = None):
        self.registry = registry or UniversalCapabilityRegistry()

    def search_substitution(
        self, capability_id: str, sample_args: Tuple[Any, ...] = ()
    ) -> List[SubstitutionCandidate]:
        """
        Executes a multi-candidate substitution search for the requested capability.
        """
        record = self.registry.get(capability_id)
        if not record:
            return []

        candidates: List[SubstitutionCandidate] = []

        # 1. Evaluate CPU Alternative
        if record.cpu_alternative is not None:
            cand = self._evaluate_candidate(
                record=record,
                candidate_func=record.cpu_alternative,
                substitution_type="CPU_AVX2",
                sample_args=sample_args,
            )
            candidates.append(cand)

        # 2. Evaluate Intel UHD iGPU Alternative
        if record.intel_igpu_alternative is not None:
            cand = self._evaluate_candidate(
                record=record,
                candidate_func=record.intel_igpu_alternative,
                substitution_type="INTEL_UHD_IGPU",
                sample_args=sample_args,
            )
            candidates.append(cand)

        # 3. Evaluate Algorithmic Replacement
        if record.algorithmic_replacement is not None:
            cand = self._evaluate_candidate(
                record=record,
                candidate_func=record.algorithmic_replacement,
                substitution_type="ALGORITHMIC_REPLACEMENT",
                sample_args=sample_args,
            )
            candidates.append(cand)

        # 4. Evaluate Software Emulation
        if record.software_emulation_alternative is not None:
            cand = self._evaluate_candidate(
                record=record,
                candidate_func=record.software_emulation_alternative,
                substitution_type="SOFTWARE_EMULATION",
                sample_args=sample_args,
            )
            candidates.append(cand)

        return candidates

    def _evaluate_candidate(
        self,
        record: CapabilityRecord,
        candidate_func: Callable[..., Any],
        substitution_type: str,
        sample_args: Tuple[Any, ...],
    ) -> SubstitutionCandidate:
        """Executes reference and candidate, measures timing, and checks 6-dimension equivalence."""
        # 1. Execute Reference
        t0 = time.perf_counter()
        try:
            if sample_args:
                ref_out = record.reference_implementation(*sample_args)
            else:
                ref_out = self._generate_default_and_run(record.reference_implementation, record.capability_id)
            ref_latency = max((time.perf_counter() - t0) * 1000.0, 1e-6)
        except Exception as e:
            ref_out = None
            ref_latency = 1.0

        # 2. Execute Candidate
        t1 = time.perf_counter()
        try:
            if sample_args:
                cand_out = candidate_func(*sample_args)
            else:
                cand_out = self._generate_default_and_run(candidate_func, record.capability_id)
            cand_latency = max((time.perf_counter() - t1) * 1000.0, 1e-6)
            exec_success = True
        except Exception as e:
            cand_out = None
            cand_latency = 9999.0
            exec_success = False

        # 3. Independent Verification
        is_verified = False
        rel_err = float("inf")
        abs_err = float("inf")
        cert_status = CapabilityCertificationStatus.FAILED_CORRECTNESS

        if exec_success:
            is_verified, rel_err, abs_err = self._verify_outputs(ref_out, cand_out)
            if is_verified:
                if rel_err == 0.0 and abs_err == 0.0:
                    cert_status = CapabilityCertificationStatus.EXACT_VERIFIED
                elif rel_err <= 1e-4:
                    cert_status = CapabilityCertificationStatus.CONTRACT_VERIFIED
                else:
                    cert_status = CapabilityCertificationStatus.APPROXIMATE_VERIFIED
            else:
                cert_status = CapabilityCertificationStatus.FAILED_CORRECTNESS

        speedup = ref_latency / cand_latency if is_verified else 0.0

        # 4. Strict 6-Dimensional Equivalence Assessment (NO MERGED SCORE!)
        equivalence_ratings = {
            EquivalenceDimension.PHYSICAL_HARDWARE.value: False,  # No physical discrete GPU exists
            EquivalenceDimension.INSTRUCTION_OR_API_EMULATION.value: True,
            EquivalenceDimension.FUNCTIONAL_EQUIVALENCE.value: bool(is_verified),
            EquivalenceDimension.MATHEMATICAL_EQUIVALENCE.value: bool(is_verified and rel_err <= 1e-4),
            EquivalenceDimension.APPLICATION_CONTRACT.value: bool(is_verified),
            EquivalenceDimension.PERFORMANCE_EQUIVALENCE.value: bool(is_verified and speedup >= 0.8),
        }

        return SubstitutionCandidate(
            capability_id=record.capability_id,
            substitution_type=substitution_type,
            observable_behavior_match=is_verified,
            requires_physical_hardware=False,
            estimated_flops=1000.0,
            estimated_memory_bytes=record.required_memory_bytes,
            measured_latency_ms=cand_latency,
            measured_speedup_vs_reference=speedup,
            is_correctness_verified=is_verified,
            verification_error_relative=rel_err,
            verification_error_absolute=abs_err,
            certification_status=cert_status,
            equivalence_ratings=equivalence_ratings,
            limitations=list(record.known_limitations),
        )

    def _generate_default_and_run(self, func: Callable, cap_id: str) -> Any:
        """Synthesizes valid benchmark inputs appropriate for the specific capability."""
        if cap_id in ["CAP_GENERAL_ARITHMETIC", "CAP_INTEGER_OPERATIONS"]:
            a = np.ones((64, 64), dtype=np.int32 if "INT" in cap_id else np.float32)
            b = np.ones((64, 64), dtype=np.int32 if "INT" in cap_id else np.float32) * 2
            return func(a, b)
        elif cap_id == "CAP_FLOATING_POINT_TRANSCENDENTAL":
            x = np.linspace(-1.0, 1.0, 1024, dtype=np.float32)
            return func(x)
        elif cap_id == "CAP_MATRIX_TENSOR_GEMM":
            a = np.ones((64, 64), dtype=np.float32)
            b = np.ones((64, 64), dtype=np.float32) * 1.5
            return func(a, b)
        elif cap_id == "CAP_PARALLEL_REDUCTIONS":
            a = np.ones(1024, dtype=np.float32)
            return func(a)
        elif cap_id == "CAP_ATOMIC_OPERATIONS":
            idx = np.array([0, 1, 0, 2], dtype=np.int32)
            val = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
            return func(idx, val, 4)
        elif cap_id == "CAP_MEMORY_ALLOCATION":
            return func(4096)
        elif cap_id == "CAP_DATA_MOVEMENT":
            return func(np.ones(128, dtype=np.float32))
        elif cap_id == "CAP_TEXTURE_SAMPLING":
            tex = np.ones((16, 16, 3), dtype=np.float32)
            return func(tex, 0.5, 0.5)
        elif cap_id == "CAP_RASTERIZATION":
            verts = np.array([[[10, 10], [20, 10], [15, 20]]], dtype=np.float32)
            return func(verts, 64, 64)
        elif cap_id == "CAP_SHADER_EXECUTION":
            pix = np.ones((32, 32), dtype=np.float32) * 0.5
            return func(pix, 1.0)
        elif cap_id == "CAP_RAY_INTERSECTION":
            ro = np.array([0.0, 0.0, -5.0], dtype=np.float32)
            rd = np.array([0.0, 0.0, 1.0], dtype=np.float32)
            sc = np.array([0.0, 0.0, 0.0], dtype=np.float32)
            return func(ro, rd, sc, 1.0)
        elif cap_id == "CAP_COORDINATE_TRANSFORMS":
            pts = np.ones((32, 4), dtype=np.float32)
            mat = np.eye(4, dtype=np.float32)
            return func(pts, mat)
        elif cap_id == "CAP_VIDEO_PROCESSING":
            frame = np.ones((32, 32), dtype=np.float32)
            return func(frame)
        elif cap_id == "CAP_ML_INFERENCE":
            x = np.ones((4, 16), dtype=np.float32)
            w1 = np.ones((16, 32), dtype=np.float32) * 0.1
            b1 = np.zeros(32, dtype=np.float32)
            w2 = np.ones((32, 8), dtype=np.float32) * 0.1
            b2 = np.zeros(8, dtype=np.float32)
            return func(x, w1, b1, w2, b2)
        elif cap_id == "CAP_QUANTIZED_COMPUTATION":
            x = np.linspace(-2.0, 2.0, 128, dtype=np.float32)
            return func(x)
        elif cap_id == "CAP_COMPRESSION_DECOMPRESSION":
            return func(b"Universal alternative computation test byte sequence")
        elif cap_id == "CAP_SYNCHRONIZATION":
            return func()
        elif cap_id == "CAP_ASYNC_EXECUTION":
            return func(lambda x: x * 2, 42)
        elif cap_id == "CAP_SPECIALIZED_TENSOR_ATTENTION":
            q = np.ones((16, 8), dtype=np.float32)
            k = np.ones((16, 8), dtype=np.float32)
            v = np.ones((16, 8), dtype=np.float32)
            return func(q, k, v)
        elif cap_id == "CAP_GRAPHICS_COMPUTE_API":
            return func("DISPATCH_COMPUTE", {"threads_x": 64})
        else:
            return func()

    def _verify_outputs(self, ref: Any, cand: Any) -> Tuple[bool, float, float]:
        """Independent differential verification comparing candidate against reference."""
        if ref is None and cand is None:
            return True, 0.0, 0.0

        if isinstance(ref, (tuple, list)) and isinstance(cand, (tuple, list)):
            if len(ref) != len(cand):
                return False, float("inf"), float("inf")
            all_valid = True
            max_rel = 0.0
            max_abs = 0.0
            for r_item, c_item in zip(ref, cand):
                v, r, a = self._verify_outputs(r_item, c_item)
                all_valid = all_valid and v
                max_rel = max(max_rel, r)
                max_abs = max(max_abs, a)
            return all_valid, max_rel, max_abs

        if isinstance(ref, np.ndarray) and isinstance(cand, np.ndarray):
            if ref.shape != cand.shape:
                return False, float("inf"), float("inf")
            abs_err = float(np.max(np.abs(ref - cand)))
            max_ref = float(np.max(np.abs(ref)))
            scale = max_ref if max_ref > 0.0 else 1.0
            rel_err = float(abs_err / scale)
            # Match if within 1e-3
            is_valid = bool(rel_err <= 1e-3 or abs_err <= 1e-4)
            return is_valid, rel_err, abs_err

        if isinstance(ref, (int, float)) and isinstance(cand, (int, float)):
            abs_err = abs(float(ref) - float(cand))
            scale = abs(float(ref)) if abs(float(ref)) > 0.0 else 1.0
            rel_err = abs_err / scale
            is_valid = bool(rel_err <= 1e-3 or abs_err <= 1e-4)
            return is_valid, rel_err, abs_err

        try:
            if ref == cand:
                return True, 0.0, 0.0
        except Exception:
            pass

        return False, float("inf"), float("inf")
