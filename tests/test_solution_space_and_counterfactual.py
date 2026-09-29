"""
tests/test_solution_space_and_counterfactual.py
===============================================
Validation suite for Phase 5 (Search Space Compiler) & Phase 6 (Counterfactual Engine).
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pytest

from hyper.discovery.cir import CIRGraph, OpType
from hyper.research_engine.contracts import ComputationalContract
from hyper.research_engine.exactness import ExactnessCategory, ExactnessMode
from hyper.research_engine.solution_space_compiler import (
    CandidatePathway,
    SolutionSpaceCompiler,
    TransformationGenerator,
)
from hyper.research_engine.counterfactual_residual import (
    CounterfactualEngine,
    CounterfactualHypothesis,
)


class CustomIdentityOptimizationGenerator(TransformationGenerator):
    @property
    def name(self) -> str:
        return "CUSTOM_SCALAR_DOUBLE_INVOLUTION"

    @property
    def category(self) -> str:
        return "ALGEBRAIC_INVOLUTION"

    def can_apply(self, candidate: CandidatePathway, contract: ComputationalContract) -> bool:
        return "GEMM" in contract.workload_id

    def apply(self, candidate: CandidatePathway, contract: ComputationalContract) -> Optional[CandidatePathway]:
        cir = candidate.cir_graph.clone()
        cir.name = f"{candidate.cir_graph.name}_involution"

        def involution_exec(inputs: Dict[str, Any]) -> Any:
            # Involution (-(-A)) @ B == A @ B
            neg_a = -inputs["A"]
            restored_a = -neg_a
            return restored_a @ inputs["B"]

        return CandidatePathway(
            candidate_id="cand_custom_involution",
            parent_id=candidate.candidate_id,
            transformation_history=candidate.transformation_history + [self.name],
            assumptions={"algebraic_ring": "true"},
            cir_graph=cir,
            cir_hash=cir.get_hash(),
            estimated_cost={"flops": 1.0, "latency_ms": 0.95},
            exactness_category=ExactnessCategory.EXACT,
            proof_obligations=["-(-A) == A"],
            executable_fn=involution_exec,
        )


def test_dynamic_transformation_generator_plugging():
    contract = ComputationalContract(
        workload_id="GEMM_STANDARD",
        description="Standard Matmul",
        input_domain={
            "A": {"shape": [32, 32], "dtype": "FP32"},
            "B": {"shape": [32, 32], "dtype": "FP32"},
        },
        output_domain={"C": {"shape": [32, 32], "dtype": "FP32"}},
        exactness_category=ExactnessCategory.EXACT,
    )

    cir = CIRGraph(name="test_gemm")
    parent = SolutionSpaceCompiler.generate_initial_candidate(contract, cir)

    # Register custom generator
    gen = CustomIdentityOptimizationGenerator()
    SolutionSpaceCompiler.register_transformation(gen)
    assert gen.name in SolutionSpaceCompiler.list_transformations()

    # Expand candidate
    children = SolutionSpaceCompiler.expand_candidate(parent, contract)
    gen_names = [c.transformation_history[-1] for c in children]
    assert gen.name in gen_names

    # Clean up
    SolutionSpaceCompiler.unregister_transformation(gen.name)


def test_counterfactual_hypotheses_generation():
    contract = ComputationalContract(
        workload_id="GEMM_STANDARD",
        description="Standard Matmul",
        input_domain={
            "A": {"shape": [64, 64], "dtype": "FP32"},
            "B": {"shape": [64, 64], "dtype": "FP32"},
        },
        output_domain={"C": {"shape": [64, 64], "dtype": "FP32"}},
        exactness_category=ExactnessCategory.NUMERICALLY_EQUIVALENT,
        tolerance_epsilon=1e-4,
    )

    cir = CIRGraph(name="gemm_cf")
    parent = SolutionSpaceCompiler.generate_initial_candidate(contract, cir)

    hypotheses = CounterfactualEngine.generate_counterfactual_hypotheses(parent, contract)
    assert len(hypotheses) >= 6

    # Verify each carries all 7 mandated fields
    for h in hypotheses:
        assert isinstance(h.hypothesis_id, str)
        assert len(h.question) > 0
        assert len(h.transformation) > 0
        assert len(h.reason) > 0
        assert isinstance(h.expected_benefit, dict)
        assert len(h.preconditions) > 0
        assert len(h.proof_obligations) > 0
        assert h.verification_status in ("UNVERIFIED", "VERIFIED", "REFUTED")


def test_counterfactual_evaluation_verified():
    contract = ComputationalContract(
        workload_id="GEMM_STANDARD",
        description="Standard Matmul",
        input_domain={
            "A": {"shape": [32, 32], "dtype": "FP32"},
            "B": {"shape": [32, 32], "dtype": "FP32"},
        },
        output_domain={"C": {"shape": [32, 32], "dtype": "FP32"}},
        exactness_category=ExactnessCategory.NUMERICALLY_EQUIVALENT,
        tolerance_epsilon=1e-3,
    )


    hyp = CounterfactualHypothesis(
        hypothesis_id="cf_test_verified",
        target_candidate_id="cand_root",
        question="What if matrix multiplication is executed with transposed inner loop?",
        transformation="INNER_LOOP_TRANSPOSE",
        reason="Preserves exact dot product with better stride-1 locality",
        expected_benefit={"latency_speedup": 1.1},
        preconditions=["Standard 2D float32 matrices"],
        proof_obligations=["A @ B == (B.T @ A.T).T"],
    )

    def valid_candidate_fn(inputs):
        return (inputs["B"].T @ inputs["A"].T).T

    ok, proof, cost = CounterfactualEngine.evaluate_hypothesis(hyp, valid_candidate_fn, contract)
    assert ok is True
    assert hyp.verification_status == "VERIFIED"
    assert "latency_ms" in cost
    assert cost["latency_ms"] > 0


def test_counterfactual_evaluation_refuted():
    contract = ComputationalContract(
        workload_id="GEMM_STANDARD",
        description="Standard Matmul",
        input_domain={
            "A": {"shape": [32, 32], "dtype": "FP32"},
            "B": {"shape": [32, 32], "dtype": "FP32"},
        },
        output_domain={"C": {"shape": [32, 32], "dtype": "FP32"}},
        exactness_category=ExactnessCategory.EXACT,
    )

    hyp = CounterfactualHypothesis(
        hypothesis_id="cf_test_bad",
        target_candidate_id="cand_root",
        question="What if we falsely claim A @ B == A + B?",
        transformation="FALSE_ADDITION_SUBSTITUTION",
        reason="Flawed hypothesis that must be refuted",
        expected_benefit={"flops_reduction": 0.99},
        preconditions=["None"],
        proof_obligations=["Matmul == Addition"],
    )

    def broken_candidate_fn(inputs):
        return inputs["A"] + inputs["B"]

    ok, proof, cost = CounterfactualEngine.evaluate_hypothesis(hyp, broken_candidate_fn, contract)
    assert ok is False
    assert hyp.verification_status == "REFUTED"
