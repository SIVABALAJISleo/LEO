"""
hyper/core/obligation/analyzer.py
Computational Obligation Analyzer & Observable Boundary Slicer (Prompt Section 5 & 12).
Determines the minimal set of mathematically necessary operations required by the contract.
Never removes an operation merely because it "looks unnecessary" — requires formal dependency proof.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np

from hyper.core.semantic_ir.models import CanonicalSemanticIR, SemanticNode, SemanticOpCode
from hyper.core.contract.models import SemanticContract, ContractType


class ObligationAnalysisReport:
    def __init__(
        self,
        required_outputs: List[str],
        required_inputs: List[str],
        observable_state: List[str],
        necessary_operations: List[str],
        removable_operations: List[str],
        reuse_candidates: List[str],
        structure_candidates: List[str],
        proof_obligations: List[str],
    ):
        self.required_outputs = required_outputs
        self.required_inputs = required_inputs
        self.observable_state = observable_state
        self.necessary_operations = necessary_operations
        self.removable_operations = removable_operations
        self.reuse_candidates = reuse_candidates
        self.structure_candidates = structure_candidates
        self.proof_obligations = proof_obligations

    def to_dict(self) -> Dict[str, Any]:
        return {
            "required_outputs": self.required_outputs,
            "required_inputs": self.required_inputs,
            "observable_state": self.observable_state,
            "necessary_operations": self.necessary_operations,
            "removable_operations": self.removable_operations,
            "reuse_candidates": self.reuse_candidates,
            "structure_candidates": self.structure_candidates,
            "proof_obligations": self.proof_obligations,
        }


class ComputationalObligationAnalyzer:
    """
    Analyzes computational obligations required to satisfy a SemanticContract.
    """

    @staticmethod
    def analyze(ir: CanonicalSemanticIR, contract: SemanticContract) -> ObligationAnalysisReport:
        # Determine observable outputs based on contract
        required_outputs = list(ir.output_nodes)
        observable_state = [out for out in required_outputs]

        # Backward dependency traversal from required outputs
        necessary_nodes: Set[str] = set()
        queue: List[str] = list(required_outputs)

        while queue:
            curr_id = queue.pop(0)
            if curr_id in necessary_nodes:
                continue
            necessary_nodes.add(curr_id)
            if curr_id in ir.nodes:
                node = ir.nodes[curr_id]
                for inp_id in node.inputs:
                    if inp_id not in necessary_nodes:
                        queue.append(inp_id)

        # Classify nodes
        required_inputs = []
        removable_operations = []
        necessary_operations = []
        reuse_candidates = []
        structure_candidates = []
        proof_obligations = []

        for node_id, node in ir.nodes.items():
            if node.opcode == SemanticOpCode.INPUT and node_id in necessary_nodes:
                required_inputs.append(node_id)
            elif node_id not in necessary_nodes and not node.has_side_effects:
                removable_operations.append(node_id)
                proof_obligations.append(f"Proof that d(Output)/d({node_id}) == 0")
            else:
                necessary_operations.append(node_id)
                if node.opcode == SemanticOpCode.MATMUL:
                    structure_candidates.append(node_id)
                    proof_obligations.append(f"Verify structural sparsity/low-rank for {node_id}")
                if node.is_constant:
                    reuse_candidates.append(node_id)

        return ObligationAnalysisReport(
            required_outputs=required_outputs,
            required_inputs=required_inputs,
            observable_state=observable_state,
            necessary_operations=necessary_operations,
            removable_operations=removable_operations,
            reuse_candidates=reuse_candidates,
            structure_candidates=structure_candidates,
            proof_obligations=proof_obligations,
        )


class OutputDirectedSlicer:
    """
    Slices the IR to only compute contract-observable values (Prompt Section 12).
    For instance: if contract only cares about argmax, avoid computing unobserved scalar elements.
    """

    @staticmethod
    def slice_for_contract(ir: CanonicalSemanticIR, contract: SemanticContract) -> CanonicalSemanticIR:
        if contract.contract_type in [ContractType.CLASSIFICATION_TOP1, ContractType.CLASSIFICATION_TOPK]:
            # Add an explicit ARGMAX or TOP_K node directly if not present
            has_argmax = any(n.opcode == SemanticOpCode.ARGMAX for n in ir.nodes.values())
            if not has_argmax and ir.output_nodes:
                last_out = ir.output_nodes[-1]
                argmax_node = SemanticNode(
                    node_id=f"argmax_{last_out}",
                    opcode=SemanticOpCode.ARGMAX,
                    inputs=[last_out],
                    shape=(1,),
                    dtype="int64",
                )
                ir.add_node(argmax_node)
                ir.output_nodes = [argmax_node.node_id]

        return ir
