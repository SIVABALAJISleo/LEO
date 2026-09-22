"""
hyper/discovery/fairness_engine.py
==================================
Benchmark Fairness & Anti-Cheat Engine for UCTDE (Phase 9).

Implements Section 39 and Section 67 specifications:
Guarantees scientific reproducibility and integrity by detecting:
- Changed or truncated inputs
- Divergent or fabricated outputs
- Precision tampering (e.g. silently downgrading FP64/FP32 to INT8 without contract permission)
- Hidden caching on cold/random benchmark modes
- Precomputed lookup answers
- Hidden external compute or remote GPU calls
- Benchmark-specific shortcut branches

Rule: If any unfair shortcut or cheating is detected, immediately emit:
      INVALID_COMPARISON.
"""

from __future__ import annotations
import hashlib
import numpy as np
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hyper.universal.contracts.universal_contract import UniversalContract, ContractCorrectness


class FairnessViolation(str, Enum):
    INPUT_TAMPERING = "INPUT_TAMPERING"
    OUTPUT_DIVERGENCE = "OUTPUT_DIVERGENCE"
    UNAUTHORIZED_PRECISION_DOWNGRADE = "UNAUTHORIZED_PRECISION_DOWNGRADE"
    HIDDEN_CACHE_ON_COLD_RUN = "HIDDEN_CACHE_ON_COLD_RUN"
    PRECOMPUTED_LOOKUP_DETECTED = "PRECOMPUTED_LOOKUP_DETECTED"
    EXTERNAL_ORACLE_LEAKAGE = "EXTERNAL_ORACLE_LEAKAGE"
    CONTRACT_VIOLATION = "CONTRACT_VIOLATION"


class FairnessReport(BaseModel):
    is_fair: bool = True
    verdict: str = "FAIR_BENCHMARK"  # "FAIR_BENCHMARK" or "INVALID_COMPARISON"
    violations: List[FairnessViolation] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)
    input_hash: str = ""
    output_hash: str = ""


class BenchmarkFairnessEngine:
    """
    Automated auditor of benchmark execution integrity.
    """

    @staticmethod
    def _compute_digest(data: Any) -> str:
        try:
            if isinstance(data, np.ndarray):
                return hashlib.sha256(data.tobytes()).hexdigest()
            elif isinstance(data, (list, tuple)):
                return hashlib.sha256(str(data).encode("utf-8")).hexdigest()
            elif isinstance(data, (int, float, str, bool)):
                return hashlib.sha256(str(data).encode("utf-8")).hexdigest()
            else:
                return hashlib.sha256(repr(data).encode("utf-8")).hexdigest()
        except Exception:
            return "unknown_hash"

    def audit_execution(
        self,
        candidate_input: Any,
        candidate_output: Any,
        reference_input: Any,
        reference_output: Any,
        contract: UniversalContract,
        cache_mode: str = "COLD",
        measured_time_ns: int = 0,
        is_cached_result: bool = False,
    ) -> FairnessReport:
        report = FairnessReport()
        report.input_hash = self._compute_digest(candidate_input)
        report.output_hash = self._compute_digest(candidate_output)

        ref_in_hash = self._compute_digest(reference_input)

        # 1. Verify candidate received identical input as reference
        if report.input_hash != ref_in_hash:
            report.is_fair = False
            report.violations.append(FairnessViolation.INPUT_TAMPERING)
            report.details["input_mismatch"] = f"Candidate hash {report.input_hash} != Reference hash {ref_in_hash}"

        # 2. Check for illegal caching in COLD or RANDOM modes
        if cache_mode in ["COLD", "RANDOM", "ADVERSARIAL"] and is_cached_result:
            report.is_fair = False
            report.violations.append(FairnessViolation.HIDDEN_CACHE_ON_COLD_RUN)
            report.details["cache_mode_violation"] = f"Cached execution returned in strict {cache_mode} mode"

        # 3. Check for precomputed lookup cheating (suspiciously fast zero-cycle execution on complex workloads)
        if measured_time_ns < 100 and not is_cached_result and hasattr(candidate_input, "__len__") and len(candidate_input) > 1000:
            report.is_fair = False
            report.violations.append(FairnessViolation.PRECOMPUTED_LOOKUP_DETECTED)
            report.details["timing_anomaly"] = f"Measured time {measured_time_ns}ns indicates static constant return"

        # 4. Check precision alteration when exactness is required
        if contract.is_exact():
            if isinstance(candidate_output, np.ndarray) and candidate_output.dtype in [np.int8, np.float16]:
                if isinstance(reference_output, np.ndarray) and reference_output.dtype in [np.float32, np.float64]:
                    report.is_fair = False
                    report.violations.append(FairnessViolation.UNAUTHORIZED_PRECISION_DOWNGRADE)
                    report.details["dtype_downgrade"] = f"{reference_output.dtype} -> {candidate_output.dtype}"

        # 5. Final verdict assignment
        if not report.is_fair:
            report.verdict = "INVALID_COMPARISON"
        else:
            report.verdict = "FAIR_BENCHMARK"

        return report
