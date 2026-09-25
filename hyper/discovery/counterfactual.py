"""
hyper/discovery/counterfactual.py
=================================
Counterfactual Engine for Computational Pathway Discovery.

Answers the fundamental question:
"What if this computation did not happen?"

Analyzes whether intermediate operations can be omitted or replaced with
a lower-cost residual correction while strictly satisfying the contract.
"""

from __future__ import annotations

import copy
import dataclasses
import uuid
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from hyper.discovery.cir import CIRGraph, CIRNode, CIREdge, CIRTensorMeta, DataType, OpType
from hyper.discovery.contract import VerificationMode, WorkloadContract
from hyper.discovery.search_space import CandidatePathway


@dataclasses.dataclass
class CounterfactualAnalysisResult:
    """Detailed analysis of removing or replacing an operation."""
    node_id: str
    node_name: str
    original_flops: float
    omission_residual_norm: float
    correction_found: bool
    correction_type: str  # "ZERO_RESIDUAL" | "SCALAR_CORRECTION" | "LOW_RANK_RESIDUAL" | "NONE"
    correction_flops: float
    net_flops_saved: float
    candidate: Optional[CandidatePathway] = None


class CounterfactualEngine:
    """
    Counterfactual Engine.
    Tests omission and residual reconstruction of intermediate operations.
    """

    def analyze_graph(
        self,
        graph: CIRGraph,
        sample_inputs: Dict[str, Any],
        contract: WorkloadContract,
    ) -> List[CounterfactualAnalysisResult]:
        """
        Evaluate every removable operation counterfactually.
        """
        results: List[CounterfactualAnalysisResult] = []

        # 1. Compute ground-truth output on sample inputs
        try:
            ref_output = graph.evaluate(sample_inputs)
        except Exception:
            return results

        # 2. Identify candidate removable nodes (exclude inputs and final outputs)
        removable_nids = [
            nid for nid, node in graph.nodes.items()
            if nid not in graph.inputs and nid not in graph.outputs and not node.attributes.get("is_constant")
        ]

        for nid in removable_nids:
            target_node = graph.nodes[nid]
            if not target_node.inputs:
                continue

            analysis = self._evaluate_omission(
                graph=graph,
                target_node=target_node,
                sample_inputs=sample_inputs,
                ref_output=ref_output,
                contract=contract,
            )
            if analysis is not None:
                results.append(analysis)

        return results

    def _evaluate_omission(
        self,
        graph: CIRGraph,
        target_node: CIRNode,
        sample_inputs: Dict[str, Any],
        ref_output: Dict[str, Any],
        contract: WorkloadContract,
    ) -> Optional[CounterfactualAnalysisResult]:
        """
        Attempt bypassing target_node and check if residual can be reconstructed cheaply.
        """
        # Create counterfactual bypass graph
        bypass_g = graph.clone()

        # Primary input feeding the target node
        primary_inp_id = target_node.inputs[0]

        # Rewire all downstream consumers of target_node to primary_inp_id
        for other in bypass_g.nodes.values():
            if other.node_id != target_node.node_id:
                other.inputs = [primary_inp_id if x == target_node.node_id else x for x in other.inputs]

        # Rewire outputs if necessary
        bypass_g.outputs = [primary_inp_id if out == target_node.node_id else out for out in bypass_g.outputs]
        bypass_g.eliminate_dead_nodes()

        # Evaluate bypassed graph
        try:
            bypassed_output = bypass_g.evaluate(sample_inputs)
        except Exception:
            # Bypass resulted in shape or evaluation incompatibility
            return None

        # Calculate residual error across outputs
        total_residual_norm = 0.0
        can_omit_directly = True

        for req in contract.required_outputs:
            if req not in ref_output or req not in bypassed_output:
                return None
            ref_val = ref_output[req]
            byp_val = bypassed_output[req]

            if isinstance(ref_val, np.ndarray) and isinstance(byp_val, np.ndarray):
                if ref_val.shape != byp_val.shape:
                    can_omit_directly = False
                    break
                diff = np.abs(ref_val - byp_val)
                norm = float(np.linalg.norm(diff.ravel()))
                total_residual_norm += norm
                max_abs = float(np.max(diff))

                # Check if within contract tolerance
                if contract.exactness_mode == VerificationMode.MODE_1_BIT_EXACT:
                    if max_abs > 0.0:
                        can_omit_directly = False
                elif contract.exactness_mode in (VerificationMode.MODE_2_NUMERIC_EXACT, VerificationMode.MODE_3_NUMERIC_TOLERANCE):
                    if max_abs > contract.tolerance_atol:
                        can_omit_directly = False
            else:
                if ref_val != byp_val:
                    can_omit_directly = False

        original_flops = target_node.estimated_flops

        # Case 1: Direct omission satisfies contract!
        if can_omit_directly:
            cand_id = f"cand_cf_omit_{uuid.uuid4().hex[:8]}"
            cand = CandidatePathway(
                candidate_id=cand_id,
                parent_id=graph.graph_id,
                graph=bypass_g,
                transformation_history=[f"Counterfactual Engine eliminated redundant operation '{target_node.name}' (saved {original_flops:.0f} FLOPs)."],
                mathematical_assumptions=[f"Downstream contract invariant satisfied with zero/negligible residual (norm={total_residual_norm:.2e})."],
                validity_conditions=["Input distribution produces outputs within contract tolerance."],
                estimated_cost=bypass_g.total_estimated_flops(),
                is_counterfactual=True,
            )
            return CounterfactualAnalysisResult(
                node_id=target_node.node_id,
                node_name=target_node.name,
                original_flops=original_flops,
                omission_residual_norm=total_residual_norm,
                correction_found=True,
                correction_type="ZERO_RESIDUAL",
                correction_flops=0.0,
                net_flops_saved=original_flops,
                candidate=cand,
            )

        # Case 2: Constant or low-rank residual correction
        # If residual has near-constant bias, add a constant offset
        if contract.exactness_mode in (VerificationMode.MODE_3_NUMERIC_TOLERANCE, VerificationMode.MODE_5_CONTRACT_EQUIVALENCE):
            for req in contract.required_outputs:
                ref_val = ref_output[req]
                byp_val = bypassed_output[req]
                if isinstance(ref_val, np.ndarray) and isinstance(byp_val, np.ndarray) and ref_val.shape == byp_val.shape:
                    diff = ref_val - byp_val
                    mean_offset = float(np.mean(diff))
                    std_offset = float(np.std(diff))
                    if std_offset <= contract.tolerance_atol:
                        # Mean offset correction is viable!
                        corrected_g = bypass_g.clone()
                        const_bias = corrected_g.add_constant(f"bias_{req}", np.float32(mean_offset))
                        req_out_node = [n for n in corrected_g.nodes.values() if n.name == req][0]
                        corr_node = corrected_g.add_op(
                            OpType.ADD,
                            [req_out_node.node_id, const_bias.node_id],
                            name=f"{req}_corrected",
                            output_meta=req_out_node.output_meta,
                        )
                        corrected_g.outputs = [corr_node.node_id if o == req_out_node.node_id else o for o in corrected_g.outputs]

                        cand_id = f"cand_cf_bias_{uuid.uuid4().hex[:8]}"
                        corr_flops = float(ref_val.size)
                        cand = CandidatePathway(
                            candidate_id=cand_id,
                            parent_id=graph.graph_id,
                            graph=corrected_g,
                            transformation_history=[f"Counterfactual Engine replaced '{target_node.name}' with scalar bias correction ({mean_offset:.4f})."],
                            mathematical_assumptions=["Residual exhibits near-uniform constant shift."],
                            validity_conditions=["Input inputs maintain uniform variance within contract bound."],
                            estimated_cost=corrected_g.total_estimated_flops(),
                            is_counterfactual=True,
                        )
                        return CounterfactualAnalysisResult(
                            node_id=target_node.node_id,
                            node_name=target_node.name,
                            original_flops=original_flops,
                            omission_residual_norm=total_residual_norm,
                            correction_found=True,
                            correction_type="SCALAR_CORRECTION",
                            correction_flops=corr_flops,
                            net_flops_saved=original_flops - corr_flops,
                            candidate=cand,
                        )

        return CounterfactualAnalysisResult(
            node_id=target_node.node_id,
            node_name=target_node.name,
            original_flops=original_flops,
            omission_residual_norm=total_residual_norm,
            correction_found=False,
            correction_type="NONE",
            correction_flops=0.0,
            net_flops_saved=0.0,
            candidate=None,
        )
