"""
hyper_x/wormhole_compiler/parity_gates.py
=============================================================================
HYPER-X Strict Parity Gates, Three-Track Separation & Baseline Integrity
=============================================================================
Enforces the mandatory scientific decoupling rules:
  1. Three Independent Tracks:
     - TRACK 1: EXACT
     - TRACK 2: NUMERICALLY APPROXIMATE
     - TRACK 3: APPLICATION / CONTRACT
  2. Cache State Separation:
     - CACHE_COLD vs CACHE_WARM (Never conflate cached lookup with uncached compute)
  3. Strict Parity Gates:
     - Exact Parity Gate
     - Numerical Parity Gate
     - Functional Parity Gate
     - Contract Parity Gate
     - Application Parity Gate
     - Performance Parity Gate
     - Resource Parity Gate
     - Conjunctive Overall Gate (Requires ALL sub-gates to pass for 100%)
  4. Baseline Integrity & Invalid Result Rejection (Phase 41):
     - Rejects any comparison where inputs differ, output shapes differ,
       cache states differ, or estimated power is labeled measured.
  5. Wormhole Score & Work Elimination Metrics (Phase 27):
     - WormholeScore = verified_necessary_work / reference_work
     - WorkElimination = 1 - WormholeScore
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple

from hyper_x.wormhole_compiler.schemas import (
    ExecutionTrack,
    CachePolicy,
    PowerTelemetryType,
    WorkloadContract,
    CorrectnessRequirement,
)


@dataclass
class BaselineIntegrityCheck:
    is_valid: bool
    status: str                        # "VALID", "INVALID"
    rejection_reasons: List[str] = field(default_factory=list)


@dataclass
class StrictParityScorecard:
    workload_id: str
    execution_track: ExecutionTrack
    cache_state: CachePolicy
    power_telemetry: PowerTelemetryType

    # Individual Parity Gates (True = PASS, False = FAIL)
    exact_parity_gate: bool = False
    numerical_parity_gate: bool = False
    functional_parity_gate: bool = False
    contract_parity_gate: bool = False
    application_parity_gate: bool = False
    performance_parity_gate: bool = False
    resource_parity_gate: bool = False
    provenance_gate: bool = False
    holdout_gate: bool = False

    # Conjunctive 100% Gate
    overall_conjunctive_gate: bool = False

    # Independent Continuous Metrics (Never combined into one number)
    wormhole_score: float = 1.0        # verified_necessary_work / reference_work (Lower is better)
    work_elimination_ratio: float = 0.0 # 1 - wormhole_score
    raw_hardware_speedup: float = 1.0  # T_ref / T_candidate
    memory_reduction_ratio: float = 0.0
    relative_numerical_error: float = 0.0

    raw_reference_latency_ms: float = 0.0
    raw_candidate_latency_ms: float = 0.0
    reference_flops: float = 0.0
    candidate_flops: float = 0.0

    baseline_integrity: BaselineIntegrityCheck = field(default_factory=lambda: BaselineIntegrityCheck(True, "VALID"))

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["execution_track"] = self.execution_track.value
        d["cache_state"] = self.cache_state.value
        d["power_telemetry"] = self.power_telemetry.value
        return d


class ParityEvaluator:
    """Evaluates strict multi-metric parity and guards baseline integrity."""

    @staticmethod
    def audit_baseline_integrity(
        ref_input_shape: Tuple[int, ...],
        cand_input_shape: Tuple[int, ...],
        ref_precision: str,
        cand_precision: str,
        ref_cache: CachePolicy,
        cand_cache: CachePolicy,
        power_type: PowerTelemetryType,
        claimed_as_measured_power: bool
    ) -> BaselineIntegrityCheck:
        reasons = []

        if ref_input_shape != cand_input_shape:
            reasons.append(f"Input shape mismatch: Reference {ref_input_shape} vs Candidate {cand_input_shape}")
        if ref_precision != cand_precision:
            reasons.append(f"Precision mismatch: Reference {ref_precision} vs Candidate {cand_precision}")
        if ref_cache != cand_cache:
            reasons.append(f"Cache state mismatch: Reference {ref_cache.value} vs Candidate {cand_cache.value}")
        if claimed_as_measured_power and power_type != PowerTelemetryType.MEASURED_POWER:
            reasons.append("Claimed 'measured power' but telemetry is estimated/unmeasured")

        is_valid = len(reasons) == 0
        return BaselineIntegrityCheck(
            is_valid=is_valid,
            status="VALID" if is_valid else "INVALID",
            rejection_reasons=reasons
        )

    @staticmethod
    def evaluate(
        contract: WorkloadContract,
        candidate_latency_ms: float,
        reference_latency_ms: float,
        numerical_error: float,
        nominal_reference_flops: float,
        actual_necessary_flops: float,
        memory_used_mb: float,
        provenance_valid: bool,
        holdout_passed: bool,
        cache_state: CachePolicy = CachePolicy.COLD,
        power_telemetry: PowerTelemetryType = PowerTelemetryType.ESTIMATED_POWER,
        functional_pass: Optional[bool] = None,
        candidate_output: Optional[Any] = None,
        reference_output: Optional[Any] = None
    ) -> StrictParityScorecard:
        """Computes all separate gates and conjunctive overall parity."""
        # 1. Exact Parity Gate
        exact_pass = (numerical_error == 0.0)

        # 2. Numerical Parity Gate
        numerical_pass = (numerical_error <= contract.tolerance)

        # 3. Functional Parity Gate (Rigorously verified, never hard-coded)
        if functional_pass is not None:
            actual_functional_pass = bool(functional_pass)
        elif candidate_output is not None:
            # Check shape, finiteness, and NaN/Inf rejection
            import numpy as np
            c_arr = np.asarray(candidate_output)
            finite_ok = bool(np.all(np.isfinite(c_arr)))
            shape_ok = True
            if reference_output is not None:
                r_arr = np.asarray(reference_output)
                shape_ok = (c_arr.shape == r_arr.shape)
            actual_functional_pass = finite_ok and shape_ok and numerical_pass
        else:
            # When outputs are abstracted, require numerical pass and holdout pass
            actual_functional_pass = numerical_pass and holdout_passed
            if contract.correctness == CorrectnessRequirement.EXACT:
                actual_functional_pass = actual_functional_pass and exact_pass

        # 4. Contract Parity Gate (Meets tolerance, SLO, and memory)
        contract_pass = (
            numerical_pass and
            actual_functional_pass and
            (candidate_latency_ms <= contract.latency_slo_ms) and
            (memory_used_mb <= contract.memory_limit_mb)
        )

        # 5. Application Parity Gate (Meets end-user SLO)
        application_pass = (candidate_latency_ms <= contract.latency_slo_ms) and numerical_pass

        # 6. Performance Parity Gate (Candidate latency <= Reference latency)
        performance_pass = (candidate_latency_ms <= reference_latency_ms)

        # 7. Resource Parity Gate (Memory <= limit)
        resource_pass = (memory_used_mb <= contract.memory_limit_mb)

        # 8. Conjunctive Overall 100% Gate
        overall_100 = (
            numerical_pass and
            actual_functional_pass and
            contract_pass and
            application_pass and
            performance_pass and
            resource_pass and
            provenance_valid and
            holdout_passed
        )
        if contract.correctness == CorrectnessRequirement.EXACT:
            overall_100 = overall_100 and exact_pass

        # 9. Wormhole Score & Work Elimination
        wormhole_score = actual_necessary_flops / max(1.0, nominal_reference_flops)
        work_elimination = max(0.0, 1.0 - wormhole_score)
        raw_speedup = reference_latency_ms / max(0.001, candidate_latency_ms)

        return StrictParityScorecard(
            workload_id=contract.workload_id,
            execution_track=contract.execution_track,
            cache_state=cache_state,
            power_telemetry=power_telemetry,
            exact_parity_gate=exact_pass,
            numerical_parity_gate=numerical_pass,
            functional_parity_gate=actual_functional_pass,
            contract_parity_gate=contract_pass,
            application_parity_gate=application_pass,
            performance_parity_gate=performance_pass,
            resource_parity_gate=resource_pass,
            provenance_gate=provenance_valid,
            holdout_gate=holdout_passed,
            overall_conjunctive_gate=overall_100,
            wormhole_score=round(wormhole_score, 4),
            work_elimination_ratio=round(work_elimination, 4),
            raw_hardware_speedup=round(raw_speedup, 2),
            relative_numerical_error=round(numerical_error, 8),
            raw_reference_latency_ms=round(reference_latency_ms, 3),
            raw_candidate_latency_ms=round(candidate_latency_ms, 3),
            reference_flops=nominal_reference_flops,
            candidate_flops=actual_necessary_flops
        )
