"""
hyper/escape_engine/workloads/polynomial.py
===========================================
VAEE Initial Research Workload: Polynomial Evaluation.

Compares:
- Naive power summation: a_0 + a_1*x + a_2*x^2 + ... (2N arithmetic ops)
- Horner's nested rule: a_0 + x*(a_1 + x*(a_2 + ...)) (N arithmetic ops)
- Verifies exact floating-point equality under contract
"""

from __future__ import annotations

import numpy as np
from typing import Any, Dict, Tuple

from ..contracts.schema import ComputationalContract
from ..verification.verifier import MasterVerifier
from ..analysis.cost_model import CostAnalyzer


class PolynomialResearchWorkload:
    """Workload evaluating algebraic reformulation of polynomials."""

    def __init__(self, degree: int = 1000, seed: int = 42) -> None:
        self.degree = degree
        self.rng = np.random.default_rng(seed)
        self.coeffs = self.rng.standard_normal(degree + 1).astype(np.float64)
        self.x = 1.001

        # Ground truth: standard Horner
        self.ref_val = float(np.polynomial.polynomial.polyval(self.x, self.coeffs))

        self.contract = ComputationalContract(
            contract_id=f"poly_eval_deg_{degree}",
            input_type="polynomial",
            output_type="scalar",
            input_shape=(degree + 1,),
            output_shape=(1,),
            correctness="NUMERICAL",
            numeric_tolerance=1e-5,
            verification_method="EXACT_DIFFERENTIAL",
        )

    def naive_evaluate(self) -> float:
        """Naive summation: computes powers x^i explicitly."""
        total = 0.0
        for i, c in enumerate(self.coeffs):
            total += c * (self.x ** i)
        return total

    def horner_evaluate(self) -> float:
        """Horner's rule: nested O(N) multiply-add."""
        res = 0.0
        for c in reversed(self.coeffs):
            res = res * self.x + c
        return res

    def run_benchmark(self) -> Dict[str, Any]:
        _, naive_cost = CostAnalyzer.measure_execution(self.naive_evaluate, trials=5)
        _, horner_cost = CostAnalyzer.measure_execution(self.horner_evaluate, trials=5)

        verifier = MasterVerifier()
        v_res = verifier.verify_candidate(self.horner_evaluate(), self.ref_val, self.contract)

        speedup = naive_cost.wall_clock_ms / max(1e-6, horner_cost.wall_clock_ms)

        return {
            "workload": f"Polynomial_Degree_{self.degree}",
            "contract": self.contract.to_dict(),
            "naive_latency_ms": naive_cost.wall_clock_ms,
            "horner_latency_ms": horner_cost.wall_clock_ms,
            "verified_speedup": round(speedup, 2),
            "verification_status": v_res.trust_level,
            "is_verified": bool(v_res.is_valid),
        }
