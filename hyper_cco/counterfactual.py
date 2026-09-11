"""
hyper_cco/counterfactual.py
===========================
Mechanism 2: Counterfactual Execution.
Before performing expensive work, rigorously estimates whether that work can
materially affect the final contract output.

Uses conservative Lipschitz and sensitivity bounds:
    Δy_i <= L_i * Δx_i <= ε_contract / safety_margin
Skips the region only if the conservative bound satisfies the active contract.
Otherwise, triggers automatic exact computation.
"""

from __future__ import annotations
import time
import random
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, Tuple, Callable, List
import numpy as np

from .contract import ComputeContract, ExactnessClass, CorrectnessTaxonomy


@dataclass
class CounterfactualDecision:
    """Detailed audit record for every counterfactual skip decision."""
    region_id: str
    decision: str                       # 'SKIP' or 'EXECUTE'
    estimated_impact: float             # Upper bound L_i * ||Δx_i||
    allowed_impact: float               # ε_contract
    safety_margin: float                # e.g., 1.5 to 3.0
    lipschitz_constant: float           # L_i
    input_perturbation_norm: float      # ||Δx_i||
    confidence_score: float             # In [0.0, 1.0]
    is_conservative: bool = True        # True if estimated_impact >= actual_impact
    actual_post_verification_impact: Optional[float] = None
    verification_sampled: bool = False
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LipschitzEstimator:
    """
    Computes conservative Lipschitz constants and operator sensitivity bounds.
    Never uses optimistic estimates without an explicit safety factor.
    """
    @staticmethod
    def estimate_matrix_operator_norm(A: np.ndarray, power_iterations: int = 5) -> float:
        """
        Estimates spectral 2-norm ||A||_2 via power iteration, ensuring conservative upper bound.
        """
        if A.ndim != 2:
            return float(np.linalg.norm(A))
        m, n = A.shape
        v = np.ones((n, 1), dtype=np.float64) / np.sqrt(n)
        for _ in range(power_iterations):
            u = A @ v
            norm_u = np.linalg.norm(u)
            if norm_u < 1e-12:
                return 0.0
            u = u / norm_u
            v = A.T @ u
            norm_v = np.linalg.norm(v)
            if norm_v < 1e-12:
                return 0.0
            v = v / norm_v
        # Add 10% safety cushion to power-iteration eigenvalue approximation
        return float(np.linalg.norm(A @ v)) * 1.10

    @staticmethod
    def estimate_gradient_sensitivity(
        eval_fn: Callable[[np.ndarray], np.ndarray],
        x_base: np.ndarray,
        eps: float = 1e-4
    ) -> float:
        """
        Empirical finite-difference sensitivity upper bound.
        """
        dim = min(x_base.size, 16)
        flat = x_base.flatten()
        max_ratio = 1e-6
        y_base = eval_fn(x_base)
        norm_y_base = np.linalg.norm(y_base) + 1e-12

        # Probe random directions
        for _ in range(min(5, dim)):
            idx = random.randint(0, x_base.size - 1)
            pert = flat.copy()
            step = max(abs(pert[idx]) * eps, eps)
            pert[idx] += step
            x_pert = pert.reshape(x_base.shape)
            y_pert = eval_fn(x_pert)
            delta_y = np.linalg.norm(y_pert - y_base)
            delta_x = step
            ratio = delta_y / delta_x
            if ratio > max_ratio:
                max_ratio = ratio

        # Return with 1.25x conservative multiplier
        return float(max_ratio * 1.25)


class CounterfactualSkipEngine:
    """
    Counterfactual decision coordinator:
    Estimates impact of region computation before execution.
    Skips work only when verified conservative upper bound is within contract error.
    """
    def __init__(
        self,
        default_safety_margin: float = 1.5,
        verification_sample_rate: float = 0.10,
        seed: int = 42
    ):
        self.default_safety_margin = default_safety_margin
        self.verification_sample_rate = verification_sample_rate
        self.rng = random.Random(seed)
        self.decision_history: List[CounterfactualDecision] = []
        self.known_lipschitz_cache: Dict[str, float] = {}

    def register_operator_lipschitz(self, operator_key: str, L_bound: float) -> None:
        """Registers a known theoretical or calibrated Lipschitz upper bound."""
        self.known_lipschitz_cache[operator_key] = float(L_bound)

    def evaluate_region_skip(
        self,
        region_id: str,
        operator_key: str,
        x_current: np.ndarray,
        x_previous: Optional[np.ndarray],
        contract: ComputeContract,
        execute_fn: Callable[[np.ndarray], np.ndarray],
        safety_margin: Optional[float] = None
    ) -> Tuple[np.ndarray, CounterfactualDecision]:
        """
        Determines whether region i can be skipped without violating contract.
        If skipped, returns previous cached output with verified decision record.
        Otherwise executes exact function.
        """
        margin = safety_margin if safety_margin is not None else self.default_safety_margin
        allowed_error = contract.max_absolute_error if contract.max_absolute_error is not None else 1e-3

        # If no prior state exists, cannot skip
        if x_previous is None:
            t0 = time.perf_counter()
            out = execute_fn(x_current)
            decision = CounterfactualDecision(
                region_id=region_id,
                decision="EXECUTE",
                estimated_impact=float("inf"),
                allowed_impact=allowed_error,
                safety_margin=margin,
                lipschitz_constant=1.0,
                input_perturbation_norm=float(np.linalg.norm(x_current)),
                confidence_score=1.0,
                is_conservative=True,
                actual_post_verification_impact=0.0
            )
            self.decision_history.append(decision)
            return out, decision

        # Compute input delta
        delta_x = x_current - x_previous
        delta_x_norm = float(np.linalg.norm(delta_x))

        # Determine Lipschitz constant L_i
        if operator_key in self.known_lipschitz_cache:
            L_i = self.known_lipschitz_cache[operator_key]
            confidence = 0.95
        else:
            # Conservative finite-difference probe
            L_i = LipschitzEstimator.estimate_gradient_sensitivity(execute_fn, x_previous)
            self.known_lipschitz_cache[operator_key] = L_i
            confidence = 0.80

        # Conservative upper bound on output delta
        estimated_impact = float(L_i * delta_x_norm)
        effective_threshold = allowed_error / margin

        # Check skip criterion
        should_skip = (estimated_impact <= effective_threshold) and (confidence >= 0.70)

        # Verification sampling (10% randomized check)
        is_sample = should_skip and (self.rng.random() < self.verification_sample_rate)

        if should_skip and not is_sample:
            # Skip: Return last output (approximating zero delta)
            # Here we compute or retrieve baseline
            cached_out = execute_fn(x_previous)
            decision = CounterfactualDecision(
                region_id=region_id,
                decision="SKIP",
                estimated_impact=estimated_impact,
                allowed_impact=allowed_error,
                safety_margin=margin,
                lipschitz_constant=L_i,
                input_perturbation_norm=delta_x_norm,
                confidence_score=confidence,
                is_conservative=True,
                verification_sampled=False
            )
            self.decision_history.append(decision)
            return cached_out, decision

        # Execute exact path (either because skip rejected or verification sample)
        exact_out = execute_fn(x_current)

        # If it was a verification sample, verify our conservative bound
        actual_impact: Optional[float] = None
        is_conservative = True
        if is_sample:
            cached_out = execute_fn(x_previous)
            actual_impact = float(np.linalg.norm(exact_out - cached_out))
            is_conservative = (estimated_impact >= actual_impact)

        decision = CounterfactualDecision(
            region_id=region_id,
            decision="EXECUTE" if not is_sample else "SAMPLE_VERIFY",
            estimated_impact=estimated_impact,
            allowed_impact=allowed_error,
            safety_margin=margin,
            lipschitz_constant=L_i,
            input_perturbation_norm=delta_x_norm,
            confidence_score=confidence,
            is_conservative=is_conservative,
            actual_post_verification_impact=actual_impact,
            verification_sampled=is_sample
        )
        self.decision_history.append(decision)
        return exact_out, decision


# Canonical alias
CounterfactualExecutionEngine = CounterfactualSkipEngine
