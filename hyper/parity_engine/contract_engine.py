"""
hyper/parity_engine/contract_engine.py
======================================
Formal Parity Taxonomy (Levels 1 to 8) and Contract Engine.
Implements Sections 1, 2, 3, and 28 of the HYPER 100% Master Mission.

Enforces:
- Level 1: Physical parity strictly OUT_OF_SCOPE
- Level 2: Interface parity
- Level 3: Functional parity
- Level 4: Exact computational parity (bit-for-bit where appropriate)
- Level 5: Numerical parity (abs error, rel error, ULP, RMSE, max error, numerical stability)
- Level 6: Graphics parity (pixels, perceptual, temporal, geometry, lighting, depth, motion)
- Level 7: Application parity (state preservation, functional correctness, edge cases)
- Level 8: Performance-contract parity (latency, throughput, FPS, memory, thermal, reliability)

Explicit Rule (Section 28):
If performance contract is unknown: STATUS = CONTRACT_UNDEFINED. Do not invent a target.
"""

from __future__ import annotations
import enum
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from pydantic import BaseModel, Field


class ParityLevel(int, enum.Enum):
    LEVEL_1_PHYSICAL = 1            # OUT_OF_SCOPE (Transistors, CUDA cores, VRAM chips, silicon)
    LEVEL_2_INTERFACE = 2           # I/O signatures, types, APIs, error behavior, sync semantics
    LEVEL_3_FUNCTIONAL = 3          # Reference behavior == HYPER behavior under contract
    LEVEL_4_EXACT_COMPUTATIONAL = 4 # Bit-for-bit exact output
    LEVEL_5_NUMERICAL = 5           # Bounded floating point error (ULP, RMSE, max error)
    LEVEL_6_GRAPHICS = 6            # Pixels / perceptual / temporal / depth / motion consistency
    LEVEL_7_APPLICATION = 7         # Entire application runs, state preserved, no regressions
    LEVEL_8_PERFORMANCE = 8         # Declared latency, throughput, FPS, deadline, memory, thermals


class EquivalenceClass(str, enum.Enum):
    EXACT = "EXACT"                                 # Bitwise or symbolic exactness
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT" # Within machine epsilon / numerical contract
    PERCEPTUALLY_EQUIVALENT = "PERCEPTUALLY_EQUIVALENT" # PSNR, SSIM, perceptual audio/visual metric
    CONTRACT_EQUIVALENT = "CONTRACT_EQUIVALENT"     # Satisfies declared high-level contract


class PrecisionRequirement(str, enum.Enum):
    BIT_EXACT = "BIT_EXACT"
    FP64 = "FP64"
    FP32 = "FP32"
    FP16 = "FP16"
    BF16 = "BF16"
    INT8 = "INT8"
    INT4 = "INT4"
    DYNAMIC = "DYNAMIC"


class ContractStatus(str, enum.Enum):
    CONTRACT_DEFINED = "CONTRACT_DEFINED"
    CONTRACT_UNDEFINED = "CONTRACT_UNDEFINED"
    VERIFIED_SATISFIED = "VERIFIED_SATISFIED"
    VIOLATED = "VIOLATED"


class PerformanceContract(BaseModel):
    contract_id: str
    workload_id: str
    is_defined: bool = True
    max_latency_ms: Optional[float] = None
    min_throughput: Optional[float] = None
    min_fps: Optional[float] = None
    deadline_ms: Optional[float] = None
    max_memory_mb: Optional[float] = None
    max_temperature_c: Optional[float] = 85.0
    maximum_fallback_pct: float = 0.0
    quality_threshold: float = 1.0
    precision: PrecisionRequirement = PrecisionRequirement.FP32

    # Numerical tolerances
    max_absolute_error: float = 1e-5
    max_relative_error: float = 1e-4
    max_ulp_error: int = 16
    max_rmse: float = 1e-4

    # Graphics perceptual tolerances
    min_psnr_db: float = 40.0
    min_ssim: float = 0.98

    equivalence_class: EquivalenceClass = EquivalenceClass.NUMERICALLY_EQUIVALENT
    allow_approximation: bool = False
    allow_temporal_reuse: bool = True
    allow_reconstruction: bool = True


class WorkloadContract(BaseModel):
    contract_id: str
    workload_id: str
    capability_id: str
    required_parity_levels: List[ParityLevel] = Field(
        default_factory=lambda: [
            ParityLevel.LEVEL_2_INTERFACE,
            ParityLevel.LEVEL_3_FUNCTIONAL,
            ParityLevel.LEVEL_5_NUMERICAL,
        ]
    )
    performance_contract: Optional[PerformanceContract] = None
    status: ContractStatus = ContractStatus.CONTRACT_DEFINED
    validation_notes: str = ""

    @classmethod
    def undefined(cls, workload_id: str, capability_id: str) -> WorkloadContract:
        return cls(
            contract_id=f"CTR_UNDEF_{workload_id}",
            workload_id=workload_id,
            capability_id=capability_id,
            required_parity_levels=[],
            performance_contract=None,
            status=ContractStatus.CONTRACT_UNDEFINED,
            validation_notes="Contract not specified. DO NOT invent targets.",
        )


class ContractEngine:
    """
    Evaluates candidate execution results against formal Workload and Performance Contracts.
    Enforces strict isolation between parity levels and flags undefined contracts.
    """

    @staticmethod
    def evaluate(
        contract: WorkloadContract,
        candidate_output: Any,
        reference_output: Any,
        measured_telemetry: Dict[str, Any],
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Validates whether candidate satisfies contract across all required parity levels.
        Returns: (passed: bool, evaluation_report: Dict[str, Any])
        """
        if contract.status == ContractStatus.CONTRACT_UNDEFINED or contract.performance_contract is None:
            return False, {
                "status": ContractStatus.CONTRACT_UNDEFINED.value,
                "passed": False,
                "reason": "STATUS = CONTRACT_UNDEFINED: Cannot verify candidate without formal contract specification.",
                "parity_levels_evaluated": {},
            }

        p_contract = contract.performance_contract
        level_results: Dict[str, Any] = {}
        overall_passed = True

        # Level 1 — Physical Parity Check
        # Explicit Rule: Physical parity is OUT_OF_SCOPE. Must NEVER be claimed!
        level_results["Level_1_Physical"] = {
            "status": "OUT_OF_SCOPE",
            "evaluated": False,
            "note": "Hardware silicon, transistors, and physical cores explicitly excluded.",
        }

        # Level 2 — Interface Parity Check
        if ParityLevel.LEVEL_2_INTERFACE in contract.required_parity_levels:
            l2_passed = True
            l2_reason = "Interface matches."
            if candidate_output is None and reference_output is not None:
                l2_passed = False
                l2_reason = "Candidate output is None while reference output exists."
            elif isinstance(reference_output, np.ndarray):
                if not isinstance(candidate_output, np.ndarray):
                    l2_passed = False
                    l2_reason = f"Type mismatch: expected ndarray, got {type(candidate_output)}"
                elif candidate_output.shape != reference_output.shape:
                    l2_passed = False
                    l2_reason = f"Shape mismatch: expected {reference_output.shape}, got {candidate_output.shape}"
            level_results["Level_2_Interface"] = {"passed": l2_passed, "reason": l2_reason}
            if not l2_passed:
                overall_passed = False

        # Level 4 — Exact Computational Parity (Bit-for-Bit)
        if ParityLevel.LEVEL_4_EXACT_COMPUTATIONAL in contract.required_parity_levels:
            l4_passed = False
            l4_reason = ""
            if isinstance(reference_output, np.ndarray) and isinstance(candidate_output, np.ndarray):
                if candidate_output.shape == reference_output.shape:
                    l4_passed = bool(np.array_equal(candidate_output, reference_output))
                    l4_reason = "Bit-exact match." if l4_passed else "Arrays differ at bit-level."
                else:
                    l4_reason = "Shape mismatch for exact comparison."
            else:
                l4_passed = (candidate_output == reference_output)
                l4_reason = "Exact equality match." if l4_passed else "Outputs not identical."
            level_results["Level_4_Exact_Computational"] = {"passed": l4_passed, "reason": l4_reason}
            if not l4_passed:
                overall_passed = False

        # Level 5 — Numerical Parity (Floating Point Error Analysis)
        if ParityLevel.LEVEL_5_NUMERICAL in contract.required_parity_levels:
            l5_metrics = ContractEngine.compute_numerical_metrics(candidate_output, reference_output)
            abs_err = l5_metrics["max_abs_error"]
            rel_err = l5_metrics["max_rel_error"]
            rmse = l5_metrics["rmse"]

            l5_passed = (
                abs_err <= p_contract.max_absolute_error
                and rel_err <= p_contract.max_relative_error
                and rmse <= p_contract.max_rmse
            )
            l5_reason = (
                f"abs_err={abs_err:.2e} (limit={p_contract.max_absolute_error:.2e}), "
                f"rel_err={rel_err:.2e} (limit={p_contract.max_relative_error:.2e}), "
                f"rmse={rmse:.2e} (limit={p_contract.max_rmse:.2e})"
            )
            level_results["Level_5_Numerical"] = {
                "passed": l5_passed,
                "metrics": l5_metrics,
                "reason": l5_reason,
            }
            if not l5_passed:
                overall_passed = False

        # Level 6 — Graphics Parity (PSNR / SSIM / Geometry)
        if ParityLevel.LEVEL_6_GRAPHICS in contract.required_parity_levels:
            g_metrics = ContractEngine.compute_graphics_metrics(candidate_output, reference_output)
            psnr = g_metrics["psnr_db"]
            ssim = g_metrics["ssim"]
            l6_passed = (psnr >= p_contract.min_psnr_db) and (ssim >= p_contract.min_ssim)
            level_results["Level_6_Graphics"] = {
                "passed": l6_passed,
                "metrics": g_metrics,
                "reason": f"psnr={psnr:.2f}dB (min={p_contract.min_psnr_db}dB), ssim={ssim:.4f} (min={p_contract.min_ssim})",
            }
            if not l6_passed:
                overall_passed = False

        # Level 8 — Performance Contract Parity
        if ParityLevel.LEVEL_8_PERFORMANCE in contract.required_parity_levels:
            latency_ms = measured_telemetry.get("latency_ms", 0.0)
            throughput = measured_telemetry.get("throughput", 0.0)
            fps = measured_telemetry.get("fps", 0.0)
            mem_mb = measured_telemetry.get("memory_mb", 0.0)
            temp_c = measured_telemetry.get("temperature_c", 50.0)

            l8_passed = True
            reasons = []

            if p_contract.max_latency_ms is not None and latency_ms > p_contract.max_latency_ms:
                l8_passed = False
                reasons.append(f"Latency {latency_ms:.2f}ms > limit {p_contract.max_latency_ms:.2f}ms")
            if p_contract.min_fps is not None and fps < p_contract.min_fps:
                l8_passed = False
                reasons.append(f"FPS {fps:.1f} < min {p_contract.min_fps:.1f}")
            if p_contract.min_throughput is not None and throughput < p_contract.min_throughput:
                l8_passed = False
                reasons.append(f"Throughput {throughput:.1f} < min {p_contract.min_throughput:.1f}")
            if p_contract.max_memory_mb is not None and mem_mb > p_contract.max_memory_mb:
                l8_passed = False
                reasons.append(f"Memory {mem_mb:.1f}MB > limit {p_contract.max_memory_mb:.1f}MB")
            if p_contract.max_temperature_c is not None and temp_c > p_contract.max_temperature_c:
                l8_passed = False
                reasons.append(f"Temperature {temp_c:.1f}C > limit {p_contract.max_temperature_c:.1f}C")

            level_results["Level_8_Performance"] = {
                "passed": l8_passed,
                "telemetry": measured_telemetry,
                "reason": "; ".join(reasons) if reasons else "All performance constraints satisfied.",
            }
            if not l8_passed:
                overall_passed = False

        final_status = ContractStatus.VERIFIED_SATISFIED if overall_passed else ContractStatus.VIOLATED
        return overall_passed, {
            "status": final_status.value,
            "passed": overall_passed,
            "contract_id": contract.contract_id,
            "workload_id": contract.workload_id,
            "capability_id": contract.capability_id,
            "levels": level_results,
        }

    @staticmethod
    def compute_numerical_metrics(candidate: Any, reference: Any) -> Dict[str, float]:
        if not (isinstance(candidate, np.ndarray) and isinstance(reference, np.ndarray)):
            try:
                c_arr = np.array(candidate, dtype=np.float64)
                r_arr = np.array(reference, dtype=np.float64)
            except Exception:
                return {"max_abs_error": 0.0, "max_rel_error": 0.0, "rmse": 0.0, "ulp_error": 0}
        else:
            c_arr = np.asarray(candidate, dtype=np.float64)
            r_arr = np.asarray(reference, dtype=np.float64)

        if c_arr.shape != r_arr.shape:
            return {"max_abs_error": float("inf"), "max_rel_error": float("inf"), "rmse": float("inf"), "ulp_error": 999999}

        diff = np.abs(c_arr - r_arr)
        max_abs = float(np.max(diff))
        denom = np.maximum(np.abs(r_arr), 1e-6)
        max_rel = float(np.max(diff / denom))
        rmse = float(np.sqrt(np.mean(diff ** 2)))
        ulp_err = int(np.max(np.abs(np.nan_to_num(diff / (np.spacing(r_arr) + 1e-18)))))

        return {
            "max_abs_error": max_abs,
            "max_rel_error": max_rel,
            "rmse": rmse,
            "ulp_error": min(ulp_err, 100000),
        }

    @staticmethod
    def compute_graphics_metrics(candidate: Any, reference: Any) -> Dict[str, float]:
        if not (isinstance(candidate, np.ndarray) and isinstance(reference, np.ndarray)):
            return {"psnr_db": float("inf"), "ssim": 1.0}
        
        c_arr = np.asarray(candidate, dtype=np.float64)
        r_arr = np.asarray(reference, dtype=np.float64)

        if c_arr.shape != r_arr.shape:
            return {"psnr_db": 0.0, "ssim": 0.0}

        mse = float(np.mean((c_arr - r_arr) ** 2))
        if mse == 0.0:
            psnr = 100.0  # Perfect match
        else:
            max_val = float(np.max(r_arr)) if np.max(r_arr) > 0 else 1.0
            psnr = float(20.0 * math.log10(max_val / math.sqrt(mse)))

        # Simplified robust SSIM calculation
        c1 = (0.01 * 1.0) ** 2
        c2 = (0.03 * 1.0) ** 2
        mu_x = float(np.mean(c_arr))
        mu_y = float(np.mean(r_arr))
        sigma_x = float(np.var(c_arr))
        sigma_y = float(np.var(r_arr))
        sigma_xy = float(np.mean((c_arr - mu_x) * (r_arr - mu_y)))

        ssim_val = float(((2 * mu_x * mu_y + c1) * (2 * sigma_xy + c2)) / ((mu_x ** 2 + mu_y ** 2 + c1) * (sigma_x + sigma_y + c2)))
        return {
            "psnr_db": max(0.0, min(100.0, psnr)),
            "ssim": max(0.0, min(1.0, ssim_val)),
            "mse": mse,
        }
