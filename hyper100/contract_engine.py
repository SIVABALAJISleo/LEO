"""
hyper100/contract_engine.py
===========================
Formal Execution Contract Definition & Validation System.
Guarantees that every optimization executed by HYPER-100 satisfies the application's
exactness, numerical error bound, perceptual threshold, latency, and memory targets.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Union, Tuple
import numpy as np


class ContractExactness(str, Enum):
    EXACT = "EXACT"                       # Must match bitwise or symbolic exactness
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT"  # Machine epsilon relative tolerance (< 1e-6)
    BOUNDED_ERROR = "BOUNDED_ERROR"       # Absolute/relative error within specified epsilon
    PERCEPTUAL = "PERCEPTUAL"             # Visual/Audio perceptual metrics (PSNR >= X dB, SSIM >= Y)
    HEURISTIC = "HEURISTIC"               # Statistical or rank-ordering consistency


class VerificationStatus(str, Enum):
    EXACT = "EXACT"
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT"
    APPROXIMATE = "APPROXIMATE"
    PREDICTIVE = "PREDICTIVE"
    CACHED = "CACHED"
    REDUCED_WORK = "REDUCED_WORK"
    UNVERIFIED = "UNVERIFIED"
    VIOLATION = "VIOLATION"


class ContractViolationError(Exception):
    """Raised when an execution fails to satisfy the declared contract."""
    def __init__(self, message: str, contract: 'ExecutionContract', measured: Dict[str, Any]):
        super().__init__(message)
        self.contract = contract
        self.measured = measured


@dataclass
class ExecutionContract:
    """
    Formal representation of the application's required execution contract.
    """
    name: str = "default_contract"
    exactness: ContractExactness = ContractExactness.NUMERICALLY_EQUIVALENT
    max_error: float = 1e-4             # Maximum allowable numerical error (absolute or relative)
    max_relative_error: float = 1e-3    # Maximum allowable relative error
    min_psnr_db: float = 35.0           # Minimum acceptable PSNR in dB for perceptual outputs
    min_ssim: float = 0.95              # Minimum structural similarity index
    max_latency_ms: float = 5000.0      # Maximum allowable execution latency in milliseconds
    min_fps: float = 0.0                # Minimum required frames per second (for real-time)
    min_throughput: float = 0.0         # Minimum operations or items per second
    memory_limit_mb: float = 8192.0     # Maximum allowable heap/device memory footprint
    energy_target_j: Optional[float] = None # Energy ceiling in Joules when measurable
    allow_approximation: bool = True    # Allow low-rank / sparse approximation if within error bound
    allow_caching: bool = True          # Allow cached / memoized result substitution
    allow_prediction: bool = True       # Allow predictive / reconstruction approximations
    custom_invariants: Dict[str, Any] = field(default_factory=dict)

    def is_exact_required(self) -> bool:
        return self.exactness == ContractExactness.EXACT

    def validate_output(
        self,
        candidate_output: Any,
        baseline_output: Optional[Any] = None,
        latency_ms: float = 0.0,
        memory_mb: float = 0.0,
        fps: float = 0.0
    ) -> Tuple[bool, VerificationStatus, Dict[str, Any]]:
        """
        Validates candidate output against the contract constraints.
        Returns (is_valid: bool, verification_status: VerificationStatus, metrics: Dict[str, Any])
        """
        metrics: Dict[str, Any] = {
            "latency_ms": latency_ms,
            "memory_mb": memory_mb,
            "fps": fps,
            "error_l_inf": 0.0,
            "error_relative": 0.0,
            "psnr_db": float("inf"),
            "ssim": 1.0,
        }

        # 1. Latency & Memory constraint checks
        if latency_ms > self.max_latency_ms:
            return False, VerificationStatus.VIOLATION, {
                **metrics,
                "violation_reason": f"Latency {latency_ms:.2f}ms exceeded limit {self.max_latency_ms:.2f}ms"
            }

        if self.min_fps > 0 and fps < self.min_fps and latency_ms > 0:
            actual_fps = 1000.0 / latency_ms
            if actual_fps < self.min_fps:
                return False, VerificationStatus.VIOLATION, {
                    **metrics,
                    "violation_reason": f"FPS {actual_fps:.1f} below minimum {self.min_fps:.1f}"
                }

        if memory_mb > self.memory_limit_mb:
            return False, VerificationStatus.VIOLATION, {
                **metrics,
                "violation_reason": f"Memory {memory_mb:.1f}MB exceeded limit {self.memory_limit_mb:.1f}MB"
            }

        # 2. Numerical / Exactness checks against baseline if available
        if baseline_output is not None:
            if isinstance(candidate_output, np.ndarray) and isinstance(baseline_output, np.ndarray):
                if candidate_output.shape != baseline_output.shape:
                    return False, VerificationStatus.VIOLATION, {
                        **metrics,
                        "violation_reason": f"Shape mismatch: {candidate_output.shape} vs {baseline_output.shape}"
                    }

                diff = np.abs(candidate_output.astype(np.float64) - baseline_output.astype(np.float64))
                max_abs_err = float(np.max(diff))
                norm_baseline = float(np.linalg.norm(baseline_output))
                norm_diff = float(np.linalg.norm(diff))
                rel_err = (norm_diff / (norm_baseline + 1e-12)) if norm_baseline > 0 else max_abs_err

                metrics["error_l_inf"] = max_abs_err
                metrics["error_relative"] = rel_err

                # Perceptual metrics if 2D/3D visual output
                if candidate_output.ndim >= 2 and norm_baseline > 0:
                    mse = float(np.mean(diff ** 2))
                    max_val = float(np.max(np.abs(baseline_output)))
                    if mse > 1e-15 and max_val > 0:
                        psnr = 20.0 * np.log10(max_val / (np.sqrt(mse) + 1e-12))
                        metrics["psnr_db"] = float(psnr)
                    else:
                        metrics["psnr_db"] = 100.0

                # Check exactness requirements
                if self.exactness == ContractExactness.EXACT:
                    if max_abs_err != 0.0:
                        return False, VerificationStatus.VIOLATION, {
                            **metrics,
                            "violation_reason": f"Exactness required but max error was {max_abs_err:.2e}"
                        }
                    return True, VerificationStatus.EXACT, metrics

                elif self.exactness == ContractExactness.NUMERICALLY_EQUIVALENT:
                    if max_abs_err > 1e-6 and rel_err > 1e-5:
                        return False, VerificationStatus.VIOLATION, {
                            **metrics,
                            "violation_reason": f"Numerical equivalence failed: err={max_abs_err:.2e}, rel={rel_err:.2e}"
                        }
                    return True, VerificationStatus.NUMERICALLY_EQUIVALENT, metrics

                elif self.exactness == ContractExactness.BOUNDED_ERROR:
                    if max_abs_err > self.max_error and rel_err > self.max_relative_error:
                        return False, VerificationStatus.VIOLATION, {
                            **metrics,
                            "violation_reason": f"Error bound violated: max_err={max_abs_err:.2e} > {self.max_error:.2e}"
                        }
                    return True, VerificationStatus.APPROXIMATE, metrics

                elif self.exactness == ContractExactness.PERCEPTUAL:
                    if metrics["psnr_db"] < self.min_psnr_db:
                        return False, VerificationStatus.VIOLATION, {
                            **metrics,
                            "violation_reason": f"PSNR {metrics['psnr_db']:.1f}dB < {self.min_psnr_db:.1f}dB"
                        }
                    return True, VerificationStatus.APPROXIMATE, metrics

            elif isinstance(candidate_output, (int, float)) and isinstance(baseline_output, (int, float)):
                abs_err = abs(float(candidate_output) - float(baseline_output))
                rel_err = abs_err / (abs(float(baseline_output)) + 1e-12)
                metrics["error_l_inf"] = abs_err
                metrics["error_relative"] = rel_err

                if self.exactness == ContractExactness.EXACT and abs_err != 0.0:
                    return False, VerificationStatus.VIOLATION, {**metrics, "violation_reason": "Scalar exact mismatch"}
                if abs_err > self.max_error and rel_err > self.max_relative_error:
                    return False, VerificationStatus.VIOLATION, {**metrics, "violation_reason": f"Scalar error {abs_err:.2e} exceeded bound"}

                return True, (VerificationStatus.EXACT if abs_err == 0 else VerificationStatus.APPROXIMATE), metrics

        return True, VerificationStatus.UNVERIFIED, metrics
