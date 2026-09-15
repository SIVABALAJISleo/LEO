"""
hyper/parity.py
===============
Ground-Truth Parity Calculation Engine for LEO/HYPER.
Fulfills Phase 15 of the Master Architectural Specification.
Separates parity into four disjoint tiers:
1. RAW_HARDWARE_PARITY
2. EXACT_COMPUTATIONAL_PARITY
3. CONTRACT_PARITY
4. APPLICATION_PARITY
Never averages quality, speed, and correctness into a misleading score.
"""

from enum import Enum
from typing import Any, Dict, Optional
from hyper.candidate import CandidateResult
from hyper.contracts.contract import Contract, validate_contract


class ParityTier(str, Enum):
    RAW_HARDWARE_PARITY = "RAW_HARDWARE_PARITY"
    EXACT_COMPUTATIONAL_PARITY = "EXACT_COMPUTATIONAL_PARITY"
    CONTRACT_PARITY = "CONTRACT_PARITY"
    APPLICATION_PARITY = "APPLICATION_PARITY"


def compute_raw_hardware_ratio(
    local_metric: float,
    reference_metric: float,
    higher_is_better: bool = False,
) -> float:
    """
    Compute physical hardware performance ratio relative to an external reference.
    For latency (lower is better): T_reference / T_local
    For throughput (higher is better): P_local / P_reference
    """
    if local_metric <= 0 or reference_metric <= 0:
        return 0.0
    if higher_is_better:
        return float(local_metric / reference_metric)
    else:
        return float(reference_metric / local_metric)


def compute_work_eliminated(
    candidate_work_units: float,
    reference_work_units: float,
) -> float:
    """
    Calculate proportion of algorithmic work eliminated:
        W_eliminated = 1 - (W_candidate / W_reference)
    Returns percentage [0.0, 100.0].
    """
    if reference_work_units <= 0:
        return 0.0
    ratio = candidate_work_units / reference_work_units
    ratio = max(0.0, min(1.0, ratio))
    return float((1.0 - ratio) * 100.0)


def compute_contract_parity(
    contract: Contract,
    result: CandidateResult,
) -> Dict[str, Any]:
    """
    Evaluate strict contract satisfaction.
    Contract parity is binary: 100.0% if and only if all conditions pass, else 0.0%.
    """
    validate_contract(contract)

    reasons_failed = []

    # 1. Exactness
    if contract.exact_required:
        if result.path_class != "EXACT" and result.path_class != "FALLBACK_EXACT":
            reasons_failed.append("exact_required is True but path_class is not EXACT")
        if result.max_abs_error is not None and result.max_abs_error > 0.0:
            reasons_failed.append(f"exact_required is True but max_abs_error is {result.max_abs_error}")

    # 2. Cache permission
    if not contract.allow_cache and result.cache_hit:
        reasons_failed.append("allow_cache is False but cache_hit occurred")

    # 3. Prediction permission
    if not contract.allow_prediction and result.prediction_used:
        reasons_failed.append("allow_prediction is False but prediction was used")

    # 4. Numerical error bounds
    if contract.max_abs_error is not None:
        if result.max_abs_error is None or result.max_abs_error > contract.max_abs_error:
            reasons_failed.append(f"max_abs_error exceeded ({result.max_abs_error} > {contract.max_abs_error})")

    if contract.max_relative_error is not None:
        if result.relative_error is None or result.relative_error > contract.max_relative_error:
            reasons_failed.append(f"max_relative_error exceeded ({result.relative_error} > {contract.max_relative_error})")

    if contract.max_rmse is not None:
        if result.rmse is None or result.rmse > contract.max_rmse:
            reasons_failed.append(f"max_rmse exceeded ({result.rmse} > {contract.max_rmse})")

    # 5. Latency bound
    if contract.max_latency_ms is not None:
        if result.latency_ms > contract.max_latency_ms:
            reasons_failed.append(f"max_latency_ms exceeded ({result.latency_ms} > {contract.max_latency_ms})")

    # 6. Perceptual metrics
    if contract.min_psnr is not None:
        psnr = result.quality_metrics.get("psnr")
        if psnr is None or psnr < contract.min_psnr:
            reasons_failed.append(f"min_psnr not met ({psnr} < {contract.min_psnr})")

    if contract.min_ssim is not None:
        ssim = result.quality_metrics.get("ssim")
        if ssim is None or ssim < contract.min_ssim:
            reasons_failed.append(f"min_ssim not met ({ssim} < {contract.min_ssim})")

    # 7. Accuracy / Recall
    if contract.min_accuracy is not None:
        acc = result.quality_metrics.get("accuracy")
        if acc is None or acc < contract.min_accuracy:
            reasons_failed.append(f"min_accuracy not met ({acc} < {contract.min_accuracy})")

    if contract.min_recall is not None:
        rec = result.quality_metrics.get("recall")
        if rec is None or rec < contract.min_recall:
            reasons_failed.append(f"min_recall not met ({rec} < {contract.min_recall})")

    passed = len(reasons_failed) == 0
    parity_pct = 100.0 if passed else 0.0

    return {
        "tier": ParityTier.CONTRACT_PARITY.value,
        "contract_name": contract.name,
        "passed": passed,
        "parity_pct": parity_pct,
        "reasons_failed": reasons_failed,
    }


def compute_application_parity(
    achieved_score: float,
    target_score: float,
    tolerance: float = 0.0,
) -> Dict[str, Any]:
    """
    Evaluate end-to-end task objective satisfaction.
    """
    satisfied = achieved_score >= (target_score - tolerance)
    return {
        "tier": ParityTier.APPLICATION_PARITY.value,
        "achieved_score": achieved_score,
        "target_score": target_score,
        "satisfied": satisfied,
        "parity_pct": 100.0 if satisfied else 0.0,
    }
