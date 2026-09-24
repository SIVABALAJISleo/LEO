"""
Computational Escape Engine: Orchestrates 7 counterfactual escape classes
(A. Elimination, B. Substitution, C. Reuse, D. Compression, E. Prediction+Correction,
 F. Representation Escape, G. Algorithmic Escape).
"""
import time
import numpy as np
from typing import Any, Callable, Dict, List, Optional, Tuple

from hyper_universal.contract_ir import ContractIR, ContractType
from hyper_universal.types import ResultTaxonomy, CacheRegime
from hyper_universal.work_meter import WorkMeter
from hyper_universal.sandbox.executor import execute_isolated_candidate
from hyper_omega.escape_engine.types import EscapeClass, EscapeHypothesis, EscapeResult


class ComputationalEscapeEngine:
    """
    Central orchestration layer asking:
    «Can this computation escape its current computational pathway?»
    """

    def __init__(self, work_meter: Optional[WorkMeter] = None):
        self.work_meter = work_meter or WorkMeter()
        self.results_history: List[EscapeResult] = []

    def generate_hypotheses(self, workload_name: str, contract: ContractIR) -> List[EscapeHypothesis]:
        """Generate counterfactual hypotheses across all 7 classes."""
        hypotheses = []

        # Class A: Elimination
        hypotheses.append(EscapeHypothesis(
            hypothesis_id=f"esc_a_{workload_name}_elim",
            escape_class=EscapeClass.A_ELIMINATION,
            description="Eliminate redundant loop iterations and dead invariant operations",
            target_operation="repeated_inner_eval",
            proposed_transformation="hoist_invariants_and_prune_dependencies",
            verification_condition="invariant_purity_proven AND outputs_identical",
            requires_exact_contract=contract.contract_type in [ContractType.EXACT, ContractType.SYMBOLIC],
            expected_work_reduction_ratio=0.5
        ))

        # Class B: Substitution
        hypotheses.append(EscapeHypothesis(
            hypothesis_id=f"esc_b_{workload_name}_subst",
            escape_class=EscapeClass.B_SUBSTITUTION,
            description="Substitute recursive or naive quadratic formula with closed-form or Horner evaluation",
            target_operation="polynomial_power_eval",
            proposed_transformation="horner_rule_substitution",
            verification_condition="algebraic_equivalence_proven",
            requires_exact_contract=True,
            expected_work_reduction_ratio=0.65
        ))

        # Class C: Reuse
        hypotheses.append(EscapeHypothesis(
            hypothesis_id=f"esc_c_{workload_name}_reuse",
            escape_class=EscapeClass.C_REUSE,
            description="Memoize pure subexpression evaluations across warm executions",
            target_operation="subexpression_eval",
            proposed_transformation="hash_memoization_cache",
            verification_condition="cache_key_collision_rate_zero",
            cache_regime=CacheRegime.WARM,
            expected_work_reduction_ratio=0.80
        ))

        # Class D: Compression
        hypotheses.append(EscapeHypothesis(
            hypothesis_id=f"esc_d_{workload_name}_compress",
            escape_class=EscapeClass.D_COMPRESSION,
            description="Compress low-entropy structures via sparse CSR or low-rank truncated SVD",
            target_operation="matrix_vector_product",
            proposed_transformation="sparse_csr_representation",
            verification_condition="frobenius_norm_error <= contract_tolerance",
            requires_exact_contract=contract.contract_type == ContractType.EXACT,
            expected_work_reduction_ratio=0.75
        ))

        # Class E: Prediction + Correction
        hypotheses.append(EscapeHypothesis(
            hypothesis_id=f"esc_e_{workload_name}_pred_corr",
            escape_class=EscapeClass.E_PREDICTION_CORRECTION,
            description="Predict coarse solution via low-order model and compute residual correction",
            target_operation="iterative_residual_step",
            proposed_transformation="linear_predictor_with_sparse_residual",
            verification_condition="residual_correction_norm <= contract_tolerance",
            requires_exact_contract=False,
            expected_work_reduction_ratio=0.45
        ))

        # Class F: Representation Escape
        hypotheses.append(EscapeHypothesis(
            hypothesis_id=f"esc_f_{workload_name}_rep_escape",
            escape_class=EscapeClass.F_REPRESENTATION_ESCAPE,
            description="Transform dense 2D spatial domain into frequency (FFT) or blocked tiled memory layout",
            target_operation="spatial_convolution",
            proposed_transformation="frequency_domain_fft_multiplication",
            verification_condition="parseval_identity_preserved",
            requires_exact_contract=True,
            expected_work_reduction_ratio=0.70
        ))

        # Class G: Algorithmic Escape
        hypotheses.append(EscapeHypothesis(
            hypothesis_id=f"esc_g_{workload_name}_algo_escape",
            escape_class=EscapeClass.G_ALGORITHMIC_ESCAPE,
            description="Replace brute-force O(N^2) or O(N^3) search with O(N log N) divide-and-conquer",
            target_operation="global_all_pairs_search",
            proposed_transformation="divide_and_conquer_strassen_or_sort",
            verification_condition="asymptotic_complexity_reduced AND contract_preserved",
            requires_exact_contract=True,
            expected_work_reduction_ratio=0.85
        ))

        return hypotheses

    def execute_and_verify_escape(
        self,
        hypothesis: EscapeHypothesis,
        candidate_code: str,
        test_inputs: List[Any],
        reference_fn: Callable[[Any], Any],
        contract: ContractIR,
    ) -> EscapeResult:
        """
        Executes a candidate escape in a sandbox and verifies its correctness.
        Crucial Rule: Reference function is NEVER called inside candidate execution.
        """
        exec_times = []
        ref_times = []
        outputs_match = True

        for inp in test_inputs:
            # Measure reference execution independently
            t0 = time.perf_counter()
            ref_out = reference_fn(inp)
            t_ref = time.perf_counter() - t0
            ref_times.append(t_ref)

            # Measure candidate execution in strict isolation
            t1 = time.perf_counter()
            res = execute_isolated_candidate(candidate_code, inp, timeout_seconds=5.0)
            t_cand = time.perf_counter() - t1
            exec_times.append(t_cand)

            if not res.success:
                return EscapeResult(
                    hypothesis_id=hypothesis.hypothesis_id,
                    escape_class=hypothesis.escape_class,
                    executed=False,
                    status=ResultTaxonomy.FAILURE,
                    measured_speedup=0.0,
                    work_eliminated_ratio=0.0,
                    verification_passed=False,
                    details={"error": res.error, "stage": "sandbox_execution"},
                    candidate_code=candidate_code
                )

            # Contract verification
            cand_out = res.output
            if contract.contract_type == ContractType.EXACT:
                if isinstance(ref_out, np.ndarray) and isinstance(cand_out, np.ndarray):
                    if not np.array_equal(ref_out, cand_out):
                        outputs_match = False
                        break
                elif ref_out != cand_out:
                    outputs_match = False
                    break
            elif contract.contract_type == ContractType.NUMERICAL_TOLERANCE:
                max_err = np.max(np.abs(np.array(ref_out) - np.array(cand_out)))
                if max_err > contract.absolute_tolerance:
                    outputs_match = False
                    break

        if not outputs_match:
            return EscapeResult(
                hypothesis_id=hypothesis.hypothesis_id,
                escape_class=hypothesis.escape_class,
                executed=True,
                status=ResultTaxonomy.COUNTEREXAMPLE_FOUND,
                measured_speedup=0.0,
                work_eliminated_ratio=0.0,
                verification_passed=False,
                details={"reason": "Contract tolerance or exact match violated"},
                candidate_code=candidate_code
            )

        avg_ref = float(np.mean(ref_times)) if ref_times else 1e-6
        avg_cand = float(np.mean(exec_times)) if exec_times else 1e-6
        speedup = avg_ref / max(avg_cand, 1e-9)
        work_elim = max(0.0, 1.0 - (avg_cand / max(avg_ref, 1e-9)))

        result = EscapeResult(
            hypothesis_id=hypothesis.hypothesis_id,
            escape_class=hypothesis.escape_class,
            executed=True,
            status=ResultTaxonomy.VERIFIED if speedup >= 1.0 else ResultTaxonomy.FOUND,
            measured_speedup=speedup,
            work_eliminated_ratio=work_elim,
            verification_passed=True,
            details={
                "avg_ref_time_ms": avg_ref * 1000.0,
                "avg_cand_time_ms": avg_cand * 1000.0,
                "cache_regime": hypothesis.cache_regime.value
            },
            candidate_code=candidate_code
        )
        self.results_history.append(result)
        return result
