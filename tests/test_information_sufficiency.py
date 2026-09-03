"""
tests/test_information_sufficiency.py
Unit tests for Information Sufficiency Analyzer, Downstream Sensitivity, and Value Density Evaluator.
"""

import pytest
import numpy as np
from information_sufficiency.analyzer import InformationSufficiencyAnalyzer, SufficiencyClass
from information_sufficiency.downstream_sensitivity import DownstreamSensitivityTracker
from information_sufficiency.value_density import ComputationValueDensityEvaluator


def test_sufficiency_analyzer_node_classification():
    # Test discardable node (no downstream consumer)
    d_discard = InformationSufficiencyAnalyzer.classify_node(
        node_name="unused_op",
        op_type="gemm",
        input_shapes=[[10, 10]],
        output_shape=[10, 10],
        is_downstream_active=False
    )
    assert d_discard.classification == SufficiencyClass.DISCARDABLE
    assert d_discard.elimination_potential == 1.0

    # Test redundant node (cached)
    d_cached = InformationSufficiencyAnalyzer.classify_node(
        node_name="cached_op",
        op_type="gemm",
        input_shapes=[[10, 10]],
        output_shape=[10, 10],
        cached_equivalent_available=True
    )
    assert d_cached.classification == SufficiencyClass.REDUNDANT
    assert d_cached.elimination_potential == 1.0

    # Test derivable node (partial top-k consumption)
    d_topk = InformationSufficiencyAnalyzer.classify_node(
        node_name="topk_op",
        op_type="sort",
        input_shapes=[[100]],
        output_shape=[100],
        consumed_indices=[0, 1, 2, 3, 4]
    )
    assert d_topk.classification == SufficiencyClass.DERIVABLE
    assert d_topk.elimination_potential > 0.5


def test_downstream_sensitivity_top_k_and_culling():
    res = DownstreamSensitivityTracker.compute_top_k_sensitivity(1000, 10)
    assert res["work_avoidance_ratio"] > 0.0
    assert res["recommended_algorithm"] == "argpartition_quickselect"

    boxes = [[-50, -50, -10, -10], [10, 10, 50, 50]]
    vis = DownstreamSensitivityTracker.compute_spatial_visibility_mask(100, 100, boxes)
    assert vis["culled_count"] == 1
    assert vis["visible_count"] == 1


def test_value_density_evaluator():
    eval_high = ComputationValueDensityEvaluator.evaluate_stage("high_val", 10.0, 1000, 10, 5.0)
    assert eval_high["value_tier"] in ["CRITICAL_VALUE", "STANDARD_VALUE"]

    ranked = ComputationValueDensityEvaluator.rank_stages([
        {"name": "s1", "info_gain": 0.01, "flops": 100000},
        {"name": "s2", "info_gain": 50.0, "flops": 500}
    ])
    assert ranked[0]["stage_name"] == "s2"
