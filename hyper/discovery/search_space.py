"""
hyper/discovery/search_space.py
===============================
Search Space Compiler for Verified Computational Pathway Discovery.

Generates candidate alternative computational pathways from CIR graphs
using formal transformation families while tracking full provenance,
mathematical assumptions, and validity conditions.
"""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import uuid
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import numpy as np

from hyper.discovery.cir import CIRGraph, CIRNode, CIREdge, CIRTensorMeta, DataType, OpType, EdgeType
from hyper.discovery.contract import VerificationMode, WorkloadContract


@dataclasses.dataclass
class CandidatePathway:
    """Represents a generated alternative computational pathway."""
    candidate_id: str
    parent_id: Optional[str]
    graph: CIRGraph
    transformation_history: List[str] = dataclasses.field(default_factory=list)
    mathematical_assumptions: List[str] = dataclasses.field(default_factory=list)
    validity_conditions: List[str] = dataclasses.field(default_factory=list)
    estimated_cost: float = 0.0
    verification_status: str = "UNVERIFIED"  # UNVERIFIED | PASSED | FAILED
    is_counterfactual: bool = False
    verification_metrics: Dict[str, Any] = dataclasses.field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "parent_id": self.parent_id,
            "transformation_history": list(self.transformation_history),
            "mathematical_assumptions": list(self.mathematical_assumptions),
            "validity_conditions": list(self.validity_conditions),
            "estimated_cost": self.estimated_cost,
            "verification_status": self.verification_status,
            "is_counterfactual": self.is_counterfactual,
            "verification_metrics": copy.deepcopy(self.verification_metrics),
            "graph": self.graph.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> CandidatePathway:
        return cls(
            candidate_id=d["candidate_id"],
            parent_id=d.get("parent_id"),
            graph=CIRGraph.from_dict(d["graph"]),
            transformation_history=list(d.get("transformation_history", [])),
            mathematical_assumptions=list(d.get("mathematical_assumptions", [])),
            validity_conditions=list(d.get("validity_conditions", [])),
            estimated_cost=float(d.get("estimated_cost", 0.0)),
            verification_status=d.get("verification_status", "UNVERIFIED"),
            is_counterfactual=bool(d.get("is_counterfactual", False)),
            verification_metrics=dict(d.get("verification_metrics", {})),
        )


class TransformRule:
    """Abstract base rule for rewriting a CIR graph."""
    rule_name: str = "base_rule"

    def is_applicable(self, graph: CIRGraph, contract: WorkloadContract) -> bool:
        raise NotImplementedError

    def apply(self, graph: CIRGraph, contract: WorkloadContract) -> List[CandidatePathway]:
        raise NotImplementedError


class RuleDeadCodeElimination(TransformRule):
    """Eliminates operations that do not contribute to final outputs."""
    rule_name = "dead_code_elimination"

    def is_applicable(self, graph: CIRGraph, contract: WorkloadContract) -> bool:
        # Check if there are dead nodes
        needed = set()
        def mark(nid: str):
            if nid in needed:
                return
            needed.add(nid)
            node = graph.nodes.get(nid)
            if node:
                for inp in node.inputs:
                    mark(inp)
        for out_id in graph.outputs:
            mark(out_id)
        return len(needed) < len(graph.nodes)

    def apply(self, graph: CIRGraph, contract: WorkloadContract) -> List[CandidatePathway]:
        new_g = graph.clone()
        removed = new_g.eliminate_dead_nodes()
        if removed == 0:
            return []

        cand_id = f"cand_dce_{uuid.uuid4().hex[:8]}"
        return [
            CandidatePathway(
                candidate_id=cand_id,
                parent_id=graph.graph_id,
                graph=new_g,
                transformation_history=[f"Dead-operation elimination removed {removed} unreferenced nodes."],
                mathematical_assumptions=["Unreferenced operations have no downstream dataflow dependency."],
                validity_conditions=["Outputs of removed nodes are not required by contract."],
                estimated_cost=new_g.total_estimated_flops(),
            )
        ]


class RuleCommonSubexpressionElimination(TransformRule):
    """Detects and merges identical operations receiving identical inputs."""
    rule_name = "common_subexpression_elimination"

    def is_applicable(self, graph: CIRGraph, contract: WorkloadContract) -> bool:
        signatures = {}
        for nid, node in graph.nodes.items():
            if node.attributes.get("is_input") or node.attributes.get("is_constant"):
                continue
            sig = (node.op_type, tuple(node.inputs), tuple(sorted(node.attributes.items())))
            if sig in signatures:
                return True
            signatures[sig] = nid
        return False

    def apply(self, graph: CIRGraph, contract: WorkloadContract) -> List[CandidatePathway]:
        new_g = graph.clone()
        signatures: Dict[Any, str] = {}
        merged_count = 0

        # Map duplicate node IDs to canonical node IDs
        remap: Dict[str, str] = {}
        for nid, node in list(new_g.nodes.items()):
            if node.attributes.get("is_input") or node.attributes.get("is_constant"):
                continue
            sig = (node.op_type, tuple(node.inputs), tuple(sorted(node.attributes.items())))
            if sig in signatures:
                canonical_id = signatures[sig]
                remap[nid] = canonical_id
                merged_count += 1
            else:
                signatures[sig] = nid

        if merged_count == 0:
            return []

        # Replace references
        for nid, node in new_g.nodes.items():
            node.inputs = [remap.get(inp, inp) for inp in node.inputs]

        # Update edges
        new_edges = []
        for e in new_g.edges:
            src = remap.get(e.source_id, e.source_id)
            tgt = remap.get(e.target_id, e.target_id)
            if src != tgt:
                new_edges.append(CIREdge(source_id=src, target_id=tgt, edge_type=e.edge_type))
        new_g.edges = new_edges

        # Update outputs if an output was remapped
        new_g.outputs = [remap.get(out_id, out_id) for out_id in new_g.outputs]

        # Delete duplicate nodes
        for dup_id in remap:
            if dup_id in new_g.nodes:
                del new_g.nodes[dup_id]

        cand_id = f"cand_cse_{uuid.uuid4().hex[:8]}"
        return [
            CandidatePathway(
                candidate_id=cand_id,
                parent_id=graph.graph_id,
                graph=new_g,
                transformation_history=[f"Common-subexpression elimination merged {merged_count} duplicate nodes."],
                mathematical_assumptions=["Operator is purely functional and deterministic without side-effects."],
                validity_conditions=["Identical inputs to deterministic operator yield bit-identical outputs."],
                estimated_cost=new_g.total_estimated_flops(),
            )
        ]


class RuleOperatorFusion(TransformRule):
    """Fuses paired operations (e.g. GEMM + Add -> FUSED_GEMM_ADD, Conv2D + ReLU -> FUSED_CONV_RELU)."""
    rule_name = "operator_fusion"

    def is_applicable(self, graph: CIRGraph, contract: WorkloadContract) -> bool:
        for nid, node in graph.nodes.items():
            if node.op_type == OpType.ADD and len(node.inputs) == 2:
                in0 = graph.nodes.get(node.inputs[0])
                in1 = graph.nodes.get(node.inputs[1])
                if (in0 and in0.op_type == OpType.MATMUL) or (in1 and in1.op_type == OpType.MATMUL):
                    return True
            elif node.op_type == OpType.RELU and len(node.inputs) == 1:
                in0 = graph.nodes.get(node.inputs[0])
                if in0 and in0.op_type in (OpType.MATMUL, OpType.CONV2D):
                    return True
        return False

    def apply(self, graph: CIRGraph, contract: WorkloadContract) -> List[CandidatePathway]:
        candidates = []
        # Attempt GEMM + ADD fusion
        for nid, node in list(graph.nodes.items()):
            if node.op_type == OpType.ADD and len(node.inputs) == 2:
                in0_id, in1_id = node.inputs[0], node.inputs[1]
                in0 = graph.nodes.get(in0_id)
                in1 = graph.nodes.get(in1_id)

                gemm_node = None
                bias_id = None
                if in0 and in0.op_type == OpType.MATMUL:
                    gemm_node = in0
                    bias_id = in1_id
                elif in1 and in1.op_type == OpType.MATMUL:
                    gemm_node = in1
                    bias_id = in0_id

                if gemm_node and bias_id:
                    new_g = graph.clone()
                    fused_id = f"fused_gemm_add_{uuid.uuid4().hex[:6]}"
                    target_name = node.name if node.node_id in graph.outputs else f"fused_{gemm_node.name}_{node.name}"
                    fused_node = CIRNode(
                        node_id=fused_id,
                        name=target_name,
                        op_type=OpType.FUSED_GEMM_ADD,
                        inputs=[gemm_node.inputs[0], gemm_node.inputs[1], bias_id],
                        output_meta=node.output_meta,
                        estimated_flops=gemm_node.estimated_flops + node.estimated_flops,
                    )
                    new_g.nodes[fused_id] = fused_node

                    # Rewire downstream users of node.node_id to fused_id
                    for other_node in new_g.nodes.values():
                        if other_node.node_id != fused_id:
                            other_node.inputs = [fused_id if x == node.node_id else x for x in other_node.inputs]

                    # Rewire outputs
                    new_g.outputs = [fused_id if out_id == node.node_id else out_id for out_id in new_g.outputs]

                    # Eliminate original Add and GEMM if not used elsewhere
                    new_g.eliminate_dead_nodes()

                    cand_id = f"cand_fuse_gemm_add_{uuid.uuid4().hex[:8]}"
                    candidates.append(
                        CandidatePathway(
                            candidate_id=cand_id,
                            parent_id=graph.graph_id,
                            graph=new_g,
                            transformation_history=[f"Fused MATMUL '{gemm_node.name}' and ADD '{node.name}' into FUSED_GEMM_ADD."],
                            mathematical_assumptions=["Associativity and distributivity of matrix addition."],
                            validity_conditions=["Intermediate GEMM result not needed by external consumer."],
                            estimated_cost=new_g.total_estimated_flops() * 0.85, # 15% cache traffic saving
                        )
                    )
                    break
        return candidates


class RuleAlgebraicReassociation(TransformRule):
    """
    Reassociates chained matrix multiplications: (A @ B) @ C vs A @ (B @ C).
    When dimensions are e.g. (1, 1024) @ (1024, 1024) @ (1024, 1), reassociation drops FLOPs by orders of magnitude.
    """
    rule_name = "algebraic_reassociation"

    def is_applicable(self, graph: CIRGraph, contract: WorkloadContract) -> bool:
        for nid, node in graph.nodes.items():
            if node.op_type == OpType.MATMUL and len(node.inputs) == 2:
                in0 = graph.nodes.get(node.inputs[0])
                if in0 and in0.op_type == OpType.MATMUL:
                    return True
        return False

    def apply(self, graph: CIRGraph, contract: WorkloadContract) -> List[CandidatePathway]:
        candidates = []
        for nid, node in graph.nodes.items():
            if node.op_type == OpType.MATMUL and len(node.inputs) == 2:
                # node = (A @ B) @ C where node.inputs[0] is (A @ B) and node.inputs[1] is C
                in0 = graph.nodes.get(node.inputs[0])
                if in0 and in0.op_type == OpType.MATMUL and len(in0.inputs) == 2:
                    A_id, B_id = in0.inputs[0], in0.inputs[1]
                    C_id = node.inputs[1]

                    # Check dimensions to verify FLOP advantage
                    A_node = graph.nodes.get(A_id)
                    B_node = graph.nodes.get(B_id)
                    C_node = graph.nodes.get(C_id)

                    if A_node and B_node and C_node and A_node.output_meta and B_node.output_meta and C_node.output_meta:
                        sA = A_node.output_meta.shape
                        sB = B_node.output_meta.shape
                        sC = C_node.output_meta.shape
                        if len(sA) == 2 and len(sB) == 2 and len(sC) == 2:
                            m, k = sA
                            _, p = sB
                            _, n = sC

                            cost_left = 2.0 * m * k * p + 2.0 * m * p * n
                            cost_right = 2.0 * k * p * n + 2.0 * m * k * n

                            if cost_right < cost_left:
                                # Construct A @ (B @ C)
                                new_g = graph.clone()
                                bc_id = f"bc_reassoc_{uuid.uuid4().hex[:6]}"
                                bc_node = new_g.add_op(
                                    OpType.MATMUL,
                                    [B_id, C_id],
                                    name=f"bc_{uuid.uuid4().hex[:4]}",
                                    output_meta=CIRTensorMeta(shape=(k, n), dtype=B_node.output_meta.dtype),
                                )
                                final_id = f"a_bc_reassoc_{uuid.uuid4().hex[:6]}"
                                target_name = node.name if node.node_id in graph.outputs else f"a_bc_{uuid.uuid4().hex[:4]}"
                                final_node = new_g.add_op(
                                    OpType.MATMUL,
                                    [A_id, bc_node],
                                    name=target_name,
                                    output_meta=node.output_meta,
                                )

                                # Rewire downstream
                                for other in new_g.nodes.values():
                                    if other.node_id not in (bc_node.node_id, final_node.node_id):
                                        other.inputs = [final_node.node_id if x == node.node_id else x for x in other.inputs]
                                new_g.outputs = [final_node.node_id if out_id == node.node_id else out_id for out_id in new_g.outputs]
                                new_g.eliminate_dead_nodes()

                                cand_id = f"cand_reassoc_{uuid.uuid4().hex[:8]}"
                                candidates.append(
                                    CandidatePathway(
                                        candidate_id=cand_id,
                                        parent_id=graph.graph_id,
                                        graph=new_g,
                                        transformation_history=[f"Reassociated (A @ B) @ C -> A @ (B @ C), reducing FLOPs from {cost_left:.0f} to {cost_right:.0f}."],
                                        mathematical_assumptions=["Associativity of matrix multiplication: (A B) C = A (B C)."],
                                        validity_conditions=["Intermediate product (A @ B) is not required elsewhere."],
                                        estimated_cost=new_g.total_estimated_flops(),
                                    )
                                )
                                break
        return candidates


class RuleSparsityExploitation(TransformRule):
    """Detects sparsity in weights or inputs and specializes the operation."""
    rule_name = "sparsity_exploitation"

    def is_applicable(self, graph: CIRGraph, contract: WorkloadContract) -> bool:
        for nid, node in graph.nodes.items():
            if node.op_type == OpType.MATMUL:
                for inp_id in node.inputs:
                    inp_node = graph.nodes.get(inp_id)
                    if inp_node and inp_node.attributes.get("is_constant") and isinstance(inp_node.constant_value, np.ndarray):
                        arr = inp_node.constant_value
                        if arr.size > 0:
                            zeros = float(np.count_nonzero(arr == 0))
                            if zeros / arr.size >= 0.40:
                                return True
        return False

    def apply(self, graph: CIRGraph, contract: WorkloadContract) -> List[CandidatePathway]:
        candidates = []
        for nid, node in graph.nodes.items():
            if node.op_type == OpType.MATMUL:
                for idx, inp_id in enumerate(node.inputs):
                    inp_node = graph.nodes.get(inp_id)
                    if inp_node and inp_node.attributes.get("is_constant") and isinstance(inp_node.constant_value, np.ndarray):
                        arr = inp_node.constant_value
                        sparsity = float(np.count_nonzero(arr == 0)) / arr.size
                        if sparsity >= 0.40:
                            new_g = graph.clone()
                            target_node = new_g.nodes[node.node_id]
                            target_node.attributes["sparsity_optimized"] = True
                            target_node.attributes["sparsity_ratio"] = sparsity
                            # Sparse FLOPs
                            target_node.estimated_flops *= (1.0 - sparsity)

                            cand_id = f"cand_sparse_{uuid.uuid4().hex[:8]}"
                            candidates.append(
                                CandidatePathway(
                                    candidate_id=cand_id,
                                    parent_id=graph.graph_id,
                                    graph=new_g,
                                    transformation_history=[f"Specialized MATMUL '{node.name}' for {sparsity*100:.1f}% sparse operand '{inp_node.name}'."],
                                    mathematical_assumptions=["Zero elements multiplied by any finite value yield zero."],
                                    validity_conditions=["Input tensor contains no NaN or Inf."],
                                    estimated_cost=new_g.total_estimated_flops(),
                                )
                            )
                            break
        return candidates


class SearchSpaceCompiler:
    """
    Search Space Compiler.
    Transforms an initial CIR graph and contract into a structured candidate pool.
    """

    def __init__(self, rules: Optional[List[TransformRule]] = None):
        self.rules: List[TransformRule] = rules or [
            RuleDeadCodeElimination(),
            RuleCommonSubexpressionElimination(),
            RuleOperatorFusion(),
            RuleAlgebraicReassociation(),
            RuleSparsityExploitation(),
        ]

    def generate_candidates(self, graph: CIRGraph, contract: WorkloadContract, max_candidates: int = 50) -> List[CandidatePathway]:
        """
        Generate candidate computational pathways through rule application.
        All candidates carry full provenance and assumptions.
        """
        candidates: List[CandidatePathway] = []

        # Always include baseline as candidate 0
        baseline_cand = CandidatePathway(
            candidate_id=f"cand_baseline_{graph.graph_id[:8]}",
            parent_id=None,
            graph=graph.clone(),
            transformation_history=["Original trusted reference pathway."],
            mathematical_assumptions=["Standard mathematical definition."],
            validity_conditions=["Standard input domain."],
            estimated_cost=graph.total_estimated_flops(),
            verification_status="UNVERIFIED",
        )
        candidates.append(baseline_cand)

        frontier = [graph]
        explored_hashes: Set[str] = {self._graph_hash(graph)}

        while frontier and len(candidates) < max_candidates:
            current_g = frontier.pop(0)

            for rule in self.rules:
                if rule.is_applicable(current_g, contract):
                    new_candidates = rule.apply(current_g, contract)
                    for cand in new_candidates:
                        ghash = self._graph_hash(cand.graph)
                        if ghash not in explored_hashes:
                            explored_hashes.add(ghash)
                            candidates.append(cand)
                            frontier.append(cand.graph)
                            if len(candidates) >= max_candidates:
                                break

        return candidates

    def _graph_hash(self, g: CIRGraph) -> str:
        """Compute structural hash of a CIR graph."""
        nodes_sig = []
        for nid in sorted(g.nodes.keys()):
            n = g.nodes[nid]
            nodes_sig.append(f"{n.name}:{n.op_type.value}:{sorted(n.inputs)}")
        payload = "|".join(nodes_sig)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
