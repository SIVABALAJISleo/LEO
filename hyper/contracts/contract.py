"""
hyper/contracts/contract.py
===========================
Formal Contract Specification and Validation System for LEO/HYPER.
Enforces mathematically sound application contracts with fail-closed validation.
Fulfills Phase 3 of the Master Architectural Specification.
"""

import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional, Union


@dataclass
class Contract:
    """Formal execution contract governing computation elimination and verification."""
    name: str
    exact_required: bool
    max_abs_error: Optional[float]
    max_relative_error: Optional[float]
    max_rmse: Optional[float]
    min_psnr: Optional[float]
    min_ssim: Optional[float]
    min_accuracy: Optional[float]
    min_recall: Optional[float]
    max_latency_ms: Optional[float]
    min_throughput: Optional[float]
    max_memory_bytes: Optional[int]
    allow_cache: bool
    allow_prediction: bool
    allow_approximation: bool
    allow_perceptual_difference: bool


def validate_contract(contract: Contract) -> bool:
    """
    Validate contract consistency.
    Raises ValueError if the contract contains contradictory or out-of-bound specifications.
    Returns True if valid.
    """
    if not isinstance(contract, Contract):
        raise ValueError(f"Expected Contract instance, got {type(contract)}")

    if not contract.name or not isinstance(contract.name, str):
        raise ValueError("Contract name must be a non-empty string.")

    # Inconsistency checks: exact execution cannot permit approximation or perceptual difference
    if contract.exact_required and contract.allow_approximation:
        raise ValueError("Invalid contract: exact_required=True and allow_approximation=True are contradictory.")

    if contract.exact_required and contract.allow_perceptual_difference:
        raise ValueError("Invalid contract: exact_required=True and allow_perceptual_difference=True are contradictory.")

    # Bound checks
    if contract.max_abs_error is not None and contract.max_abs_error < 0:
        raise ValueError(f"max_abs_error must be non-negative, got {contract.max_abs_error}")

    if contract.max_relative_error is not None and contract.max_relative_error < 0:
        raise ValueError(f"max_relative_error must be non-negative, got {contract.max_relative_error}")

    if contract.max_rmse is not None and contract.max_rmse < 0:
        raise ValueError(f"max_rmse must be non-negative, got {contract.max_rmse}")

    if contract.min_psnr is not None and contract.min_psnr < 0:
        raise ValueError(f"min_psnr must be non-negative, got {contract.min_psnr}")

    if contract.min_ssim is not None and not (0.0 <= contract.min_ssim <= 1.0):
        raise ValueError(f"min_ssim must be within [0, 1], got {contract.min_ssim}")

    if contract.min_accuracy is not None and not (0.0 <= contract.min_accuracy <= 1.0):
        raise ValueError(f"min_accuracy must be within [0, 1], got {contract.min_accuracy}")

    if contract.min_recall is not None and not (0.0 <= contract.min_recall <= 1.0):
        raise ValueError(f"min_recall must be within [0, 1], got {contract.min_recall}")

    if contract.max_latency_ms is not None and contract.max_latency_ms <= 0:
        raise ValueError(f"max_latency_ms must be positive, got {contract.max_latency_ms}")

    if contract.min_throughput is not None and contract.min_throughput <= 0:
        raise ValueError(f"min_throughput must be positive, got {contract.min_throughput}")

    if contract.max_memory_bytes is not None and contract.max_memory_bytes <= 0:
        raise ValueError(f"max_memory_bytes must be positive, got {contract.max_memory_bytes}")

    return True


def contract_to_json(contract: Contract, indent: Optional[int] = 2) -> str:
    """Serialize a Contract instance to a JSON string."""
    validate_contract(contract)
    return json.dumps(asdict(contract), indent=indent)


def contract_from_json(data: Union[str, Dict[str, Any]]) -> Contract:
    """Deserialize a JSON string or dict into a validated Contract instance."""
    if isinstance(data, str):
        payload = json.loads(data)
    elif isinstance(data, dict):
        payload = data
    else:
        raise ValueError(f"Expected str or dict, got {type(data)}")

    expected_fields = {
        "name", "exact_required", "max_abs_error", "max_relative_error",
        "max_rmse", "min_psnr", "min_ssim", "min_accuracy", "min_recall",
        "max_latency_ms", "min_throughput", "max_memory_bytes",
        "allow_cache", "allow_prediction", "allow_approximation",
        "allow_perceptual_difference"
    }

    filtered = {k: payload.get(k) for k in expected_fields}
    contract = Contract(**filtered)
    validate_contract(contract)
    return contract
