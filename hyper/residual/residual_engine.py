"""
hyper/residual/residual_engine.py
=================================
Predictive and Residual Correction Engine for LEO/HYPER.
Fulfills Phase 10 of the Master Architectural Specification.
Implements: y = y_hat + r with contract verification and fail-closed exact fallback.
"""

import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np
from hyper.candidate import PathClass


class PredictiveResidualEngine:
    """
    Coordinates prediction, residual correction, and exact fallback
    under strict contract compliance.
    """

    def __init__(self):
        # Rolling telemetry
        self.total_invocations = 0
        self.prediction_acceptances = 0
        self.residual_corrections = 0
        self.fallbacks = 0
        self.prediction_errors: List[float] = []
        self.residual_densities: List[float] = []
        self.latencies_ms: List[float] = []

    def execute_pipeline(
        self,
        current_input: Any,
        previous_state: Optional[Any],
        predictor_fn: Callable[[Optional[Any], Any], Any],
        error_estimator_fn: Callable[[Any, Any], float],
        verifier_fn: Callable[[Any, float], Tuple[bool, float]],
        residual_fn: Callable[[Any, Any], Tuple[Any, float]], # returns (residual, cost_ms)
        exact_fallback_fn: Callable[[Any], Tuple[Any, float]], # returns (result, cost_ms)
        max_allowed_error: float = 0.01,
        allow_prediction: bool = True,
        allow_residual: bool = True,
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Executes:
        1. Predict: y_hat = predictor(prev, curr)
        2. If error <= max_allowed_error and verified: return y_hat
        3. Else compute residual: corrected = y_hat + residual
        4. If verified: return corrected
        5. Else fallback to exact_fallback(curr)
        """
        t0 = time.perf_counter_ns()
        self.total_invocations += 1

        # Step 1: Predict
        if allow_prediction:
            t_pred_start = time.perf_counter_ns()
            prediction = predictor_fn(previous_state, current_input)
            t_pred_ms = (time.perf_counter_ns() - t_pred_start) / 1e6

            estimated_err = float(error_estimator_fn(prediction, current_input))
            self.prediction_errors.append(estimated_err)

            if estimated_err <= max_allowed_error:
                accepted, verified_err = verifier_fn(prediction, max_allowed_error)
                if accepted:
                    t_total_ms = (time.perf_counter_ns() - t0) / 1e6
                    self.prediction_acceptances += 1
                    self.latencies_ms.append(t_total_ms)

                    telemetry = {
                        "path_class": PathClass.PREDICTIVE.value,
                        "latency_ms": t_total_ms,
                        "prediction_used": True,
                        "residual_used": False,
                        "fallback_used": False,
                        "prediction_error": estimated_err,
                        "verified_error": verified_err,
                        "residual_density": None,
                        "residual_cost_ms": 0.0,
                    }
                    return prediction, telemetry
        else:
            prediction = None
            estimated_err = float("inf")

        # Step 2: Residual Correction
        if allow_residual and prediction is not None:
            residual, t_res_ms = residual_fn(current_input, prediction)
            
            # Calculate residual density if array
            if isinstance(residual, np.ndarray):
                res_density = float(np.count_nonzero(residual) / max(1, residual.size))
            else:
                res_density = 1.0
            self.residual_densities.append(res_density)

            corrected = prediction + residual
            accepted, verified_err = verifier_fn(corrected, max_allowed_error)
            if accepted:
                t_total_ms = (time.perf_counter_ns() - t0) / 1e6
                self.residual_corrections += 1
                self.latencies_ms.append(t_total_ms)

                telemetry = {
                    "path_class": PathClass.REDUCED_WORK.value,
                    "latency_ms": t_total_ms,
                    "prediction_used": True,
                    "residual_used": True,
                    "fallback_used": False,
                    "prediction_error": estimated_err,
                    "verified_error": verified_err,
                    "residual_density": res_density,
                    "residual_cost_ms": t_res_ms,
                }
                return corrected, telemetry

        # Step 3: Exact Fallback
        t_fb_start = time.perf_counter_ns()
        fallback_val, _ = exact_fallback_fn(current_input)
        t_total_ms = (time.perf_counter_ns() - t0) / 1e6
        self.fallbacks += 1
        self.latencies_ms.append(t_total_ms)

        telemetry = {
            "path_class": PathClass.FALLBACK_EXACT.value,
            "latency_ms": t_total_ms,
            "prediction_used": False,
            "residual_used": False,
            "fallback_used": True,
            "prediction_error": estimated_err,
            "verified_error": 0.0,
            "residual_density": None,
            "residual_cost_ms": 0.0,
        }
        return fallback_val, telemetry

    def report_metrics(self) -> Dict[str, Any]:
        """Produce cumulative metrics."""
        n = max(1, self.total_invocations)
        return {
            "total_invocations": self.total_invocations,
            "prediction_acceptance_rate": self.prediction_acceptances / n,
            "residual_correction_rate": self.residual_corrections / n,
            "fallback_rate": self.fallbacks / n,
            "mean_prediction_error": float(np.mean(self.prediction_errors)) if self.prediction_errors else 0.0,
            "mean_residual_density": float(np.mean(self.residual_densities)) if self.residual_densities else 0.0,
            "mean_latency_ms": float(np.mean(self.latencies_ms)) if self.latencies_ms else 0.0,
        }


# Alias for backward compatibility
ResidualComputationEngine = PredictiveResidualEngine
