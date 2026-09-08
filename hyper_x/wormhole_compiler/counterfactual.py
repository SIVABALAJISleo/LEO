"""
hyper_x/wormhole_compiler/counterfactual.py
=============================================================================
HYPER-X Counterfactual Computation Engine: Generative Pathway Hypotheses
=============================================================================
For every expensive node in the information dependency graph, poses 25 foundational
counterfactual questions to discover alternative computation pathways:
  1. What if this operation did not execute at all? (Removal / Dead code)
  2. What if only a fraction executed? (Partial / Sampling)
  3. What if output were predicted? (Speculation)
  4. What if previous output were reused? (Temporal caching)
  5. What if representation changed? (Sparse / Low-rank / Spectral / Quantized)
  6. What if operation were reordered? (Associativity / Commutativity)
  7. What if factorized? (Bilinear / Kronecker / SVD)
  8. What if compressed? (Entropy / Coordinate packing)
  9. What if only an observable projection were calculated? (Output projection)
 10. What if computation were event-triggered? (Threshold deltas)
 11. What if a correction term were calculated instead? (Residual Y = P + R)
 12. What if executed at lower precision followed by exact correction?
 13. What if a sufficient statistic replaced the intermediate?
 14. What if output could be reconstructed from sparse samples? (Bilateral / Upscale)
 15. What if problem had hidden low-dimensional manifold structure?
 16. What if solved recursively? (Morton / Multigrid)
 17. What if transformed to another domain? (FFT / DCT / Wavelet)
 18. What if only temporal deltas were updated? (State delta)
 19. What if decomposed into independent regions? (Domain decomposition)
 20. What if communication could be avoided? (Communication-avoiding tile)
 21. What if memory movement could be eliminated? (Kernel fusion / zero-copy)
 22. What if compute were traded for memory? (Precomputed tables / LUT)
 23. What if memory were traded for recomputation? (Rematerialization)
 24. What if a learned surrogate were paired with deterministic verification?
 25. What if structured zeros were skipped dynamically? (Dynamic zero-skipping)
"""

from __future__ import annotations
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np

from hyper_x.wormhole_compiler.schemas import (
    CounterfactualHypothesis,
    MutationType,
    DependencyNode,
    WorkloadContract,
)


class CounterfactualEngine:
    """Generates and manages counterfactual transformation hypotheses."""

    def __init__(self):
        self.hypothesis_registry: Dict[str, CounterfactualHypothesis] = {}

    def generate_hypotheses(
        self,
        node: DependencyNode,
        contract: WorkloadContract,
        workload_context: Dict[str, Any]
    ) -> List[CounterfactualHypothesis]:
        """Systematically formulates counterfactual questions for an expensive node."""
        hypotheses = []
        nid = node.node_id

        # 1. Counterfactual: Output Projection (Avoid forming intermediate)
        if workload_context.get("has_downstream_projection", False):
            hypotheses.append(CounterfactualHypothesis(
                hypothesis_id=f"HYP_PROJ_{nid}",
                target_node_id=nid,
                mutation=MutationType.OUTPUT_PROJECT,
                question="What if only the observable projection is calculated rather than full intermediate?",
                proposed_transformation="reorder_associativity_to_vector_projection",
                expected_work_reduction=0.99,
                expected_memory_reduction=0.99,
                applicable_conditions=["downstream_is_vector_or_top_k"],
                estimated_risk=0.01
            ))

        # 2. Counterfactual: Temporal / State Delta
        if contract.cache_policy.value == "WARM" or workload_context.get("has_prior_state", False):
            hypotheses.append(CounterfactualHypothesis(
                hypothesis_id=f"HYP_DELTA_{nid}",
                target_node_id=nid,
                mutation=MutationType.DELTA_COMPUTE,
                question="What if only state deltas are computed instead of full re-evaluation?",
                proposed_transformation="incremental_state_delta_update",
                expected_work_reduction=0.85,
                expected_memory_reduction=0.70,
                applicable_conditions=["temporal_similarity_gt_0.8"],
                estimated_risk=0.1
            ))

        # 3. Counterfactual: Low-Rank Factorization + Residual Correction
        if workload_context.get("estimated_rank_ratio", 1.0) < 0.6:
            hypotheses.append(CounterfactualHypothesis(
                hypothesis_id=f"HYP_LOW_RANK_{nid}",
                target_node_id=nid,
                mutation=MutationType.FACTORIZE,
                question="What if the operation is factorized into low-rank subspace plus sparse residual?",
                proposed_transformation="subspace_projection_plus_energy_residual",
                expected_work_reduction=0.70,
                expected_memory_reduction=0.50,
                applicable_conditions=["rank_ratio_lt_0.6"],
                estimated_risk=0.15
            ))

        # 4. Counterfactual: Dynamic Sparsity Zero-Skipping
        if workload_context.get("sparsity_ratio", 0.0) > 0.35:
            hypotheses.append(CounterfactualHypothesis(
                hypothesis_id=f"HYP_SPARSE_{nid}",
                target_node_id=nid,
                mutation=MutationType.REPRESENTATION_CHANGE,
                question="What if zero and sub-threshold coordinates are dynamically skipped?",
                proposed_transformation="threshold_coordinate_pruning",
                expected_work_reduction=workload_context.get("sparsity_ratio", 0.5),
                expected_memory_reduction=workload_context.get("sparsity_ratio", 0.5) * 0.8,
                applicable_conditions=["sparsity_gt_0.35"],
                estimated_risk=0.05
            ))

        # 5. Counterfactual: Recursive Cache-Oblivious Blocking
        hypotheses.append(CounterfactualHypothesis(
            hypothesis_id=f"HYP_RECURSE_{nid}",
            target_node_id=nid,
            mutation=MutationType.RECURSE,
            question="What if operation ordering follows a cache-oblivious Morton space-filling curve?",
            proposed_transformation="morton_z_order_recursive_decomposition",
            expected_work_reduction=0.25,
            expected_memory_reduction=0.40,
            applicable_conditions=["working_set_exceeds_l2_cache"],
            estimated_risk=0.01
        ))

        # 6. Counterfactual: Frequency Domain FFT
        if workload_context.get("is_convolution_or_stencil", False):
            hypotheses.append(CounterfactualHypothesis(
                hypothesis_id=f"HYP_SPECTRAL_{nid}",
                target_node_id=nid,
                mutation=MutationType.DOMAIN_TRANSFORM,
                question="What if spatial convolution is converted into pointwise spectral multiplication via FFT?",
                proposed_transformation="fast_fourier_pointwise_transform",
                expected_work_reduction=0.80,
                expected_memory_reduction=0.30,
                applicable_conditions=["kernel_size_gt_5x5"],
                estimated_risk=0.05
            ))

        # 7. Counterfactual: Sufficient Statistic Substitution
        if workload_context.get("downstream_needs_summary", False):
            hypotheses.append(CounterfactualHypothesis(
                hypothesis_id=f"HYP_SUFF_STAT_{nid}",
                target_node_id=nid,
                mutation=MutationType.SUFFICIENT_STATISTIC,
                question="What if the intermediate matrix is replaced by sufficient moments (mean, cov)?",
                proposed_transformation="moment_aggregation_bypass",
                expected_work_reduction=0.95,
                expected_memory_reduction=0.95,
                applicable_conditions=["downstream_is_statistical"],
                estimated_risk=0.05
            ))

        # 8. Counterfactual: Lower Precision with Deterministic Correction
        if contract.tolerance >= 1e-4:
            hypotheses.append(CounterfactualHypothesis(
                hypothesis_id=f"HYP_INT8_CORR_{nid}",
                target_node_id=nid,
                mutation=MutationType.LOWER_PRECISION_CORRECT,
                question="What if executed in INT8/quantized arithmetic followed by residual correction?",
                proposed_transformation="quantized_accumulator_plus_residual_refine",
                expected_work_reduction=0.50,
                expected_memory_reduction=0.60,
                applicable_conditions=["contract_permits_quantization"],
                estimated_risk=0.1
            ))

        for h in hypotheses:
            self.hypothesis_registry[h.hypothesis_id] = h

        return hypotheses
