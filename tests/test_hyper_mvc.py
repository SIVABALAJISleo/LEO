"""
tests/test_hyper_mvc.py
Unit tests for Minimum Verified Computation (MVC) Cost Evaluator, Fallback Ladder,
Break-Even Analyzer, Dataflow Optimizer, and Metamorphic Testing.
"""

import pytest
import numpy as np
from hyper_v3.mvc.cost_evaluator import MVCCostEvaluator, TotalWorkRecord
from hyper_v3.mvc.fallback_ladder import FallbackLadder, FallbackLevel
from hyper_v3.mvc.break_even import BreakEvenAnalyzer
from hyper_v3.memory.dataflow_optimizer import DataflowOptimizer
from hyper_v3.runtime.predict_verify_accept import PredictVerifyAcceptEngine
from hyper_v3.verification.metamorphic import MetamorphicVerifier


def test_mvc_cost_evaluator():
    base = TotalWorkRecord(arithmetic_flops=10000, memory_bytes=2000, transfer_bytes=500)
    cand = TotalWorkRecord(arithmetic_flops=3000, memory_bytes=1000, transfer_bytes=0)
    eval_res = MVCCostEvaluator.evaluate(base, cand)
    assert eval_res["is_beneficial"] is True
    assert eval_res["verified_work_avoidance_ratio"] > 0.0


def test_fallback_ladder():
    dispatchers = {
        FallbackLevel.LEVEL_1_EXACT_SIMPLIFICATION: lambda: "fail_result",
        FallbackLevel.LEVEL_8_EXACT_FALLBACK: lambda: "gold_result"
    }

    # Verifier fails Level 1, forces degradation to Level 8
    def verifier(res):
        return res == "gold_result"

    exec_res = FallbackLadder.execute_with_ladder("test_op", dispatchers, verifier)
    assert exec_res["passed"] is True
    assert exec_res["final_executed_level"] == int(FallbackLevel.LEVEL_8_EXACT_FALLBACK)
    assert exec_res["result"] == "gold_result"


def test_break_even_and_dataflow():
    sp_be = BreakEvenAnalyzer.calculate_sparsity_break_even(160.0)
    assert 0.5 <= sp_be <= 0.95

    pts = np.ones((10, 3))
    soa = DataflowOptimizer.convert_aos_to_soa(pts)
    assert "x" in soa and "y" in soa and "z" in soa
    assert len(soa["x"]) == 10


def test_predict_verify_accept_and_metamorphic():
    pred_fn = lambda: (np.ones((4, 4)), 0.95)
    verif_fn = lambda x: bool(np.all(x == 1.0))
    fb_fn = lambda: np.zeros((4, 4))

    out, stats = PredictVerifyAcceptEngine.execute_adaptive(pred_fn, verif_fn, fb_fn, confidence_threshold=0.90)
    assert stats["path_executed"] == "PREDICTION_ACCEPTED"
    assert stats["verified"] is True

    kernel = lambda x: x * 3.0
    arr = np.random.randn(8, 8)
    assert MetamorphicVerifier.test_scale_linearity(kernel, arr) is True
