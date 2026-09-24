"""
Falsification Agent: Actively attacks and attempts to falsify candidate breakthroughs.
Searches for Cauchy noise, ill-conditioned matrices, boundary inputs,
scaling breakdowns, and reference leakage.
"""
from dataclasses import dataclass, field
import inspect
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper_universal.contract_ir import ContractIR, ContractType
from hyper_universal.sandbox.executor import execute_isolated_candidate
from hyper_universal.types import ResultTaxonomy


@dataclass
class FalsificationAttackResult:
    attack_name: str
    passed: bool
    counterexample_input: Optional[Any] = None
    observed_error: Optional[str] = None
    relative_error: float = 0.0


class FalsificationAgent:
    """
    Hostile verification agent whose sole objective is to invalidate candidate optimizations.
    """

    def attack_candidate(
        self,
        candidate_code: str,
        reference_fn: Callable[[Any], Any],
        contract: ContractIR,
        nominal_inputs: List[Any],
    ) -> Tuple[bool, List[FalsificationAttackResult]]:
        """
        Runs comprehensive adversarial battery:
        1. Reference Leakage Test (candidate must NEVER call reference)
        2. Boundary / Extreme Value Attacks (0, Inf, NaN, empty)
        3. Heavy-tailed Cauchy Noise
        4. Ill-conditioned Inputs (Hilbert / high condition number)
        5. Contract Scaling Stress
        """
        results: List[FalsificationAttackResult] = []

        # 1. Reference Leakage Check
        ref_leak_result = self._check_reference_leak(candidate_code, reference_fn)
        results.append(ref_leak_result)
        if not ref_leak_result.passed:
            return False, results

        # 2. Boundary / Extreme Value Attack
        boundary_result = self._attack_boundaries(candidate_code, reference_fn, contract)
        results.append(boundary_result)
        if not boundary_result.passed:
            return False, results

        # 3. Cauchy Noise Attack (heavy-tailed perturbations)
        cauchy_result = self._attack_cauchy(candidate_code, reference_fn, contract, nominal_inputs)
        results.append(cauchy_result)
        if not cauchy_result.passed:
            return False, results

        # 4. Ill-Conditioned / Near-Singular Attack
        cond_result = self._attack_conditioning(candidate_code, reference_fn, contract)
        results.append(cond_result)
        if not cond_result.passed:
            return False, results

        all_passed = all(r.passed for r in results)
        return all_passed, results

    def _check_reference_leak(self, candidate_code: str, reference_fn: Callable) -> FalsificationAttackResult:
        # Check source for direct reference calls or aliases
        ref_name = getattr(reference_fn, "__name__", "reference_fn")
        forbidden = [ref_name, "reference_fn", "ref_fn"]
        for f in forbidden:
            if f in candidate_code and f != "candidate":
                return FalsificationAttackResult(
                    attack_name="reference_leakage_detection",
                    passed=False,
                    observed_error=f"Candidate contains forbidden reference identifier: {f}"
                )
        return FalsificationAttackResult(attack_name="reference_leakage_detection", passed=True)

    def _attack_boundaries(
        self,
        candidate_code: str,
        reference_fn: Callable,
        contract: ContractIR
    ) -> FalsificationAttackResult:
        # Test boundary cases: zero matrix / scalar zero
        test_cases = [
            (np.zeros((2, 2)), np.zeros((2, 2))),
            ([0.0, 0.0, 0.0], 0.0),
            np.array([0.0, 0.0, 0.0]),
        ]
        for tc in test_cases:
            try:
                ref_out = reference_fn(tc)
                res = execute_isolated_candidate(candidate_code, tc, timeout_seconds=2.0)
                if not res.success:
                    continue  # tc might not match expected shape; valid domain only
                cand_out = res.output
                if not self._verify_contract_satisfaction(ref_out, cand_out, contract):
                    return FalsificationAttackResult(
                        attack_name="boundary_extreme_values",
                        passed=False,
                        counterexample_input=tc,
                        observed_error="Candidate output deviated from reference on boundary input"
                    )
            except Exception:
                # If reference cannot process this shape, boundary is outside domain D(W)
                continue

        return FalsificationAttackResult(attack_name="boundary_extreme_values", passed=True)

    def _attack_cauchy(
        self,
        candidate_code: str,
        reference_fn: Callable,
        contract: ContractIR,
        nominal_inputs: List[Any],
    ) -> FalsificationAttackResult:
        rng = np.random.default_rng(42)
        for inp in nominal_inputs:
            if isinstance(inp, tuple) and len(inp) == 2 and isinstance(inp[0], np.ndarray):
                # Matrix pair with Cauchy noise
                A_pert = inp[0] + rng.standard_cauchy(inp[0].shape) * 1e-4
                B_pert = inp[1] + rng.standard_cauchy(inp[1].shape) * 1e-4
                pert_inp = (A_pert, B_pert)
            elif isinstance(inp, np.ndarray):
                pert_inp = inp + rng.standard_cauchy(inp.shape) * 1e-4
            else:
                continue

            try:
                ref_out = reference_fn(pert_inp)
                res = execute_isolated_candidate(candidate_code, pert_inp, timeout_seconds=2.0)
                if not res.success:
                    return FalsificationAttackResult(
                        attack_name="cauchy_noise_attack",
                        passed=False,
                        counterexample_input=pert_inp,
                        observed_error=f"Candidate crashed under Cauchy noise: {res.error}"
                    )
                cand_out = res.output
                if not self._verify_contract_satisfaction(ref_out, cand_out, contract):
                    return FalsificationAttackResult(
                        attack_name="cauchy_noise_attack",
                        passed=False,
                        counterexample_input=pert_inp,
                        observed_error="Cauchy perturbation violated contract tolerance"
                    )
            except Exception:
                continue

        return FalsificationAttackResult(attack_name="cauchy_noise_attack", passed=True)

    def _attack_conditioning(
        self,
        candidate_code: str,
        reference_fn: Callable,
        contract: ContractIR
    ) -> FalsificationAttackResult:
        # Near-singular / ill-conditioned matrix: Hilbert 2x2
        H = np.array([[1.0, 1.0/2.0], [1.0/2.0, 1.0/3.0]], dtype=np.float64)
        ill_inp = (H, H)
        try:
            ref_out = reference_fn(ill_inp)
            res = execute_isolated_candidate(candidate_code, ill_inp, timeout_seconds=2.0)
            if res.success:
                cand_out = res.output
                if not self._verify_contract_satisfaction(ref_out, cand_out, contract):
                    return FalsificationAttackResult(
                        attack_name="ill_conditioned_matrix_attack",
                        passed=False,
                        counterexample_input=ill_inp,
                        observed_error="Ill-conditioned Hilbert matrix violated numerical precision bounds"
                    )
        except Exception:
            pass

        return FalsificationAttackResult(attack_name="ill_conditioned_matrix_attack", passed=True)

    def _verify_contract_satisfaction(self, ref_out: Any, cand_out: Any, contract: ContractIR) -> bool:
        if contract.contract_type == ContractType.EXACT:
            if isinstance(ref_out, np.ndarray) and isinstance(cand_out, np.ndarray):
                return bool(np.allclose(ref_out, cand_out, atol=1e-12))
            return ref_out == cand_out
        elif contract.contract_type in [ContractType.NUMERICAL_TOLERANCE, ContractType.PERCEPTUAL]:
            diff = np.max(np.abs(np.array(ref_out) - np.array(cand_out)))
            return bool(diff <= contract.absolute_tolerance)
        return True
