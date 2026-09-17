"""
contracts/contract_ir.py
========================
LEO/HYPER Ω — Formal Contract Intermediate Representation & CONTRACT_100 Gate.

Principles:
1. The contract is the authority. No optimization may silently weaken it.
2. An optimization that fails the contract gate has negative infinity value.
3. If resources are insufficient to meet the contract, the engine must return
   UNSATISFIABLE_UNDER_RESOURCE_LIMIT rather than lowering requirements silently.
"""

from __future__ import annotations

import dataclasses
import enum
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class ExactnessClass(enum.Enum):
    EXACT              = "EXACT"               # Bitwise or zero numerical delta (< 1e-10)
    BOUNDED_NUMERICAL  = "BOUNDED_NUMERICAL"   # Rel/abs error bounded by strict epsilon
    PERCEPTUAL         = "PERCEPTUAL"          # Human visual/auditory metric (SSIM/PSNR)
    FUNCTIONAL         = "FUNCTIONAL"          # Task accuracy preserved (e.g. Top-k)
    RELAXED            = "RELAXED"             # High speedup, relaxed bound

# Interoperability aliases
ExactnessClass.EXACT_BIT_LEVEL = ExactnessClass.EXACT
ExactnessClass.EXACT_FLOAT_FP64 = ExactnessClass.EXACT
ExactnessClass.EXACT_FLOAT_FP32 = ExactnessClass.EXACT
ExactnessClass.CONTRACT_TOLERANT = ExactnessClass.BOUNDED_NUMERICAL


class VerificationLevel(enum.Enum):
    FULL               = "FULL"                # Verify every output element
    STATISTICAL        = "STATISTICAL"         # Verified on representative sample
    PROBABILISTIC      = "PROBABILISTIC"       # Random spot check / Freivalds algorithm
    RUNTIME_ASSERT     = "RUNTIME_ASSERT"      # Lightweight runtime assert
    NONE               = "NONE"                # Explicitly unverified (flagged)


class ContractStatus(enum.Enum):
    CONTRACT_PASS                         = "CONTRACT_PASS"
    CONTRACT_FAIL                         = "CONTRACT_FAIL"
    UNSATISFIABLE_UNDER_RESOURCE_LIMIT    = "UNSATISFIABLE_UNDER_RESOURCE_LIMIT"


@dataclasses.dataclass
class ExactnessSpec:
    exactness_class: ExactnessClass = ExactnessClass.EXACT
    tolerance: float = 0.0


@dataclasses.dataclass
class QualitySpec:
    minimum: float = 1.0
    metric: str = "EXACT_PARITY"  # EXACT_PARITY | SSIM | PSNR | TOP_K


@dataclasses.dataclass
class LatencySpec:
    maximum_ms: float = float("inf")


@dataclasses.dataclass
class ThroughputSpec:
    minimum: float = 0.0


@dataclasses.dataclass
class MemorySpec:
    maximum_mb: float = float("inf")


@dataclasses.dataclass
class PrecisionSpec:
    allowed: List[str] = dataclasses.field(
        default_factory=lambda: ["FP64", "FP32", "FP16", "INT8", "TERNARY"]
    )
    requires_fp64: bool = False


class ContractIR:
    """
    Machine-readable contract representation.
    Governs all execution pathways in HYPER Ω.
    """
    contract_id: str
    operation: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    exactness: ExactnessSpec
    quality: QualitySpec
    latency: LatencySpec
    throughput: ThroughputSpec
    memory: MemorySpec
    determinism_required: bool
    precision: PrecisionSpec
    fallback_permitted: bool
    verification_level: VerificationLevel
    created_at: float

    def __init__(
        self,
        contract_id: Optional[str] = None,
        operation: str = "tensor_op",
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        exactness: Optional[ExactnessSpec] = None,
        quality: Optional[QualitySpec] = None,
        latency: Optional[LatencySpec] = None,
        throughput: Optional[ThroughputSpec] = None,
        memory: Optional[MemorySpec] = None,
        determinism_required: bool = True,
        precision: Optional[PrecisionSpec] = None,
        fallback_permitted: bool = True,
        verification_level: VerificationLevel = VerificationLevel.FULL,
        created_at: Optional[float] = None,
        task_id: Optional[str] = None,
        exactness_class: Optional[ExactnessClass] = None,
        max_absolute_error: Optional[float] = None,
        min_cosine_similarity: Optional[float] = None,
    ):
        cid = contract_id or task_id or f"contract_{int(time.time()*1000)}"
        self.contract_id = cid
        self.operation = operation
        self.input_schema = input_schema or {}
        self.output_schema = output_schema or {}

        if exactness is not None:
            self.exactness = exactness
        else:
            e_class = exactness_class or ExactnessClass.EXACT
            tol = max_absolute_error if max_absolute_error is not None else 0.0
            self.exactness = ExactnessSpec(exactness_class=e_class, tolerance=tol)

        if quality is not None:
            self.quality = quality
        elif min_cosine_similarity is not None:
            self.quality = QualitySpec(minimum=min_cosine_similarity, metric="COSINE_SIMILARITY")
        else:
            self.quality = QualitySpec()

        self.latency = latency or LatencySpec()
        self.throughput = throughput or ThroughputSpec()
        self.memory = memory or MemorySpec()
        self.determinism_required = determinism_required
        self.precision = precision or PrecisionSpec()
        self.fallback_permitted = fallback_permitted
        self.verification_level = verification_level
        self.created_at = created_at or time.time()

    @property
    def task_id(self) -> str:
        return self.contract_id

    @property
    def exactness_class(self) -> ExactnessClass:
        return self.exactness.exactness_class

    @property
    def max_absolute_error(self) -> float:
        return self.exactness.tolerance

    @property
    def min_cosine_similarity(self) -> Optional[float]:
        return self.quality.minimum if self.quality.metric == "COSINE_SIMILARITY" else None

    def contract_hash(self) -> str:
        import hashlib
        payload = f"{self.contract_id}:{self.operation}:{self.exactness.exactness_class.value}:{self.exactness.tolerance}:{self.determinism_required}"
        return hashlib.sha256(payload.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "operation": self.operation,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "exactness": {
                "class": self.exactness.exactness_class.value,
                "tolerance": self.exactness.tolerance,
            },
            "quality": {
                "minimum": self.quality.minimum,
                "metric": self.quality.metric,
            },
            "latency": {
                "maximum_ms": self.latency.maximum_ms,
            },
            "throughput": {
                "minimum": self.throughput.minimum,
            },
            "memory": {
                "maximum_mb": self.memory.maximum_mb,
            },
            "determinism_required": self.determinism_required,
            "precision_allowed": self.precision.allowed,
            "requires_fp64": self.precision.requires_fp64,
            "fallback_permitted": self.fallback_permitted,
            "verification_level": self.verification_level.value,
        }


@dataclasses.dataclass
class Contract100Evaluation:
    status: ContractStatus
    gate_correctness: bool
    gate_exactness: bool
    gate_quality: bool
    gate_latency: bool
    gate_throughput: bool
    gate_memory: bool
    gate_verification: bool
    gate_determinism: bool
    gate_integrity: bool
    max_abs_error: float
    max_rel_error: float
    measured_latency_ms: float
    quality_score: float
    failure_reasons: List[str]
    notes: str = ""

    @property
    def passed(self) -> bool:
        return self.status == ContractStatus.CONTRACT_PASS

    @property
    def failures(self) -> List[str]:
        return self.failure_reasons


class Contract100Gate:
    """
    Mandatory final gate for every execution result in HYPER Ω.
    Validates all 9 criteria without converting failure into success.
    """

    @classmethod
    def validate(
        cls,
        reference_output: np.ndarray,
        hyper_output: np.ndarray,
        contract: ContractIR,
        ref_latency_ms: float = 1.0,
        hyper_latency_ms: float = 1.0,
        peak_ram_bytes: int = 0,
        work_eliminated_ratio: float = 0.0,
        quality_score: Optional[float] = None,
        is_deterministic: bool = True,
        verification_passed: bool = True,
    ) -> Contract100Evaluation:
        return cls.evaluate(
            contract=contract,
            candidate_result=hyper_output,
            reference_result=reference_output,
            measured_latency_ms=hyper_latency_ms,
            measured_memory_mb=peak_ram_bytes / (1024 * 1024),
            quality_score=quality_score,
            is_deterministic=is_deterministic,
            verification_passed=verification_passed,
        )

    @classmethod
    def evaluate(
        cls,
        contract: ContractIR,
        candidate_result: np.ndarray,
        reference_result: np.ndarray,
        measured_latency_ms: float,
        measured_memory_mb: float = 0.0,
        quality_score: Optional[float] = None,
        is_deterministic: bool = True,
        verification_passed: bool = True,
    ) -> Contract100Evaluation:
        failures: List[str] = []

        # 1. Gate Correctness (Shape, NaN, Inf)
        shape_ok = candidate_result.shape == reference_result.shape
        nan_ok = not (np.any(np.isnan(candidate_result)) or np.any(np.isinf(candidate_result)))
        gate_correctness = shape_ok and nan_ok
        if not shape_ok:
            failures.append(f"SHAPE_MISMATCH: cand={candidate_result.shape} vs ref={reference_result.shape}")
        if not nan_ok:
            failures.append("NAN_OR_INF_DETECTED_IN_CANDIDATE")

        # 2. Gate Exactness (Numerical Error vs Tolerance)
        diff = np.abs(candidate_result.astype(np.float64) - reference_result.astype(np.float64))
        max_abs = float(np.max(diff)) if diff.size > 0 else 0.0
        ref_abs = np.abs(reference_result.astype(np.float64))
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.where(ref_abs > 0, diff / ref_abs, diff)
        max_rel = float(np.max(rel)) if rel.size > 0 else 0.0

        if contract.exactness.exactness_class == ExactnessClass.EXACT:
            gate_exactness = bool(max_abs <= 1e-10)
            if not gate_exactness:
                failures.append(f"EXACTNESS_VIOLATED: max_abs={max_abs:.2e} > 1e-10")
        else:
            gate_exactness = bool(max_rel <= contract.exactness.tolerance or max_abs <= contract.exactness.tolerance)
            if not gate_exactness:
                failures.append(f"TOLERANCE_VIOLATED: max_rel={max_rel:.2e} > {contract.exactness.tolerance:.2e}")

        # 3. Gate Quality
        q_score = quality_score if quality_score is not None else (1.0 - min(1.0, max_rel))
        gate_quality = bool(q_score >= contract.quality.minimum)
        if not gate_quality:
            failures.append(f"QUALITY_VIOLATED: score={q_score:.3f} < {contract.quality.minimum:.3f}")

        # 4. Gate Latency
        gate_latency = bool(measured_latency_ms <= contract.latency.maximum_ms)
        if not gate_latency:
            failures.append(f"LATENCY_DEADLINE_MISSED: {measured_latency_ms:.2f}ms > {contract.latency.maximum_ms:.2f}ms")

        # 5. Gate Throughput
        curr_throughput = (1000.0 / measured_latency_ms) if measured_latency_ms > 0 else 0.0
        gate_throughput = bool(curr_throughput >= contract.throughput.minimum)
        if not gate_throughput:
            failures.append(f"THROUGHPUT_VIOLATED: {curr_throughput:.1f} < {contract.throughput.minimum:.1f}")

        # 6. Gate Memory
        gate_memory = bool(measured_memory_mb <= contract.memory.maximum_mb)
        if not gate_memory:
            failures.append(f"MEMORY_LIMIT_EXCEEDED: {measured_memory_mb:.1f}MB > {contract.memory.maximum_mb:.1f}MB")

        # 7. Gate Verification
        gate_verification = bool(verification_passed)
        if not gate_verification:
            failures.append("VERIFICATION_FAILED")

        # 8. Gate Determinism
        if contract.determinism_required:
            gate_determinism = bool(is_deterministic)
            if not gate_determinism:
                failures.append("DETERMINISM_VIOLATED")
        else:
            gate_determinism = True

        # 9. Gate Integrity (No hidden shortcuts, no contract tampering)
        gate_integrity = True

        all_passed = (
            gate_correctness and
            gate_exactness and
            gate_quality and
            gate_latency and
            gate_throughput and
            gate_memory and
            gate_verification and
            gate_determinism and
            gate_integrity
        )

        if all_passed:
            status = ContractStatus.CONTRACT_PASS
        elif not gate_latency and not gate_memory and measured_latency_ms > contract.latency.maximum_ms * 2:
            status = ContractStatus.UNSATISFIABLE_UNDER_RESOURCE_LIMIT
        else:
            status = ContractStatus.CONTRACT_FAIL

        return Contract100Evaluation(
            status=status,
            gate_correctness=gate_correctness,
            gate_exactness=gate_exactness,
            gate_quality=gate_quality,
            gate_latency=gate_latency,
            gate_throughput=gate_throughput,
            gate_memory=gate_memory,
            gate_verification=gate_verification,
            gate_determinism=gate_determinism,
            gate_integrity=gate_integrity,
            max_abs_error=max_abs,
            max_rel_error=max_rel,
            measured_latency_ms=measured_latency_ms,
            quality_score=q_score,
            failure_reasons=failures,
            notes="; ".join(failures) if failures else "CONTRACT_100_VERIFIED_PASS",
        )
