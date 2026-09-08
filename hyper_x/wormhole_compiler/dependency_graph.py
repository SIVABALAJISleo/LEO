"""
hyper_x/wormhole_compiler/dependency_graph.py
=============================================================================
HYPER-X Information Dependency Graph: Backward Causal Influence Analysis
=============================================================================
Constructs a causal directed graph from INPUT through TRANSFORMATIONS and
INTERMEDIATE STATES to the REQUIRED OBSERVABLE.

Performs backward dependency analysis to determine which operations actually
influence the required observable and classifies nodes into 10 strict categories:
  - INDISPENSABLE:        Directly determines output within required tolerance
  - CONDITIONALLY_REQUIRED: Executed only if trigger or residual threshold exceeded
  - REDUNDANT:            Provably dead or cancelled computation
  - REUSABLE:             Static or slowly-varying state amenable to memoization
  - PREDICTABLE:          High spatial/temporal correlation amenable to cheap extrapolation
  - APPROXIMABLE:         Tolerates lower precision or rank reduction
  - COMPRESSIBLE:         High entropy-redundancy or sparsity
  - REORDERABLE:          Commutative or associative reordering reduces intermediate rank
  - REPLACEABLE:          Cheaper algebraic alternative exists
  - UNOBSERVED:           Unreachable from the backward cone of the required observable
"""

from __future__ import annotations
from typing import Dict, List, Set, Optional, Tuple, Any
import numpy as np
from hyper_x.wormhole_compiler.schemas import (
    DependencyNode,
    NecessityClass,
    WorkloadContract,
    ObservableRequirement,
)


class InformationDependencyGraph:
    """Directed causal dependency graph with backward influence analysis."""

    def __init__(self, graph_id: str):
        self.graph_id = graph_id
        self.nodes: Dict[str, DependencyNode] = {}
        self.adj_outgoing: Dict[str, List[str]] = {}
        self.adj_incoming: Dict[str, List[str]] = {}

    def add_node(self, node: DependencyNode) -> None:
        self.nodes[node.node_id] = node
        self.adj_outgoing.setdefault(node.node_id, [])
        self.adj_incoming.setdefault(node.node_id, [])

    def add_edge(self, source_id: str, target_id: str) -> None:
        if source_id not in self.nodes or target_id not in self.nodes:
            raise KeyError(f"Both nodes must exist before adding edge: {source_id} -> {target_id}")
        self.adj_outgoing[source_id].append(target_id)
        self.adj_incoming[target_id].append(source_id)

    def backward_reachability_closure(self, observable_node_ids: List[str]) -> Set[str]:
        """
        Traverses backward from required observable nodes to determine the essential causal cone.
        Any node outside this cone is strictly UNOBSERVED.
        """
        visited: Set[str] = set()
        stack: List[str] = list(observable_node_ids)

        while stack:
            curr = stack.pop()
            if curr in visited:
                continue
            visited.add(curr)
            for predecessor in self.adj_incoming.get(curr, []):
                if predecessor not in visited:
                    stack.append(predecessor)

        return visited

    def prune_unobserved_nodes(self, observable_node_ids: List[str]) -> int:
        """Marks any node not in the backward reachability cone as UNOBSERVED."""
        cone = self.backward_reachability_closure(observable_node_ids)
        pruned_count = 0
        for nid, node in self.nodes.items():
            if nid not in cone:
                node.necessity = NecessityClass.UNOBSERVED
                node.observability = 0.0
                pruned_count += 1
        return pruned_count

    def classify_matrix_workload(
        self,
        A: np.ndarray,
        B: np.ndarray,
        contract: WorkloadContract,
        observable: ObservableRequirement
    ) -> None:
        """
        Populates and classifies nodes for a matrix multiplication operation
        under the specified contract and observable requirement.
        """
        M, K = A.shape
        _, N = B.shape
        nominal_flops = 2.0 * M * K * N

        # 1. Input Node A
        a_sparsity = float(np.mean(np.abs(A) < 1e-5))
        u, s, _ = np.linalg.svd(A, full_matrices=False)
        eff_rank = int(np.sum(s > (s[0] * 1e-3)))
        rank_ratio = eff_rank / max(1, min(M, K))

        self.add_node(DependencyNode(
            node_id="input_A",
            operation="tensor_input_A",
            estimated_cost=0.0,
            memory_cost=A.nbytes,
            dependencies=[],
            output_shape=(M, K),
            precision="float32",
            reuse_probability=0.2,
            observability=1.0,
            necessity=NecessityClass.INDISPENSABLE,
            approximation_sensitivity=0.8
        ))

        # 2. Input Node B
        self.add_node(DependencyNode(
            node_id="input_B",
            operation="tensor_input_B",
            estimated_cost=0.0,
            memory_cost=B.nbytes,
            dependencies=[],
            output_shape=(K, N),
            precision="float32",
            reuse_probability=0.2,
            observability=1.0,
            necessity=NecessityClass.INDISPENSABLE,
            approximation_sensitivity=0.8
        ))

        # 3. Intermediate GEMM Node
        gemm_necessity = NecessityClass.INDISPENSABLE
        if observable.output_type == "VECTOR":
            # Output projection wormhole! Full GEMM is redundant/reorderable
            gemm_necessity = NecessityClass.REORDERABLE
        elif a_sparsity > 0.40:
            gemm_necessity = NecessityClass.COMPRESSIBLE
        elif rank_ratio < 0.40:
            gemm_necessity = NecessityClass.APPROXIMABLE
        elif contract.cache_policy.value == "WARM":
            gemm_necessity = NecessityClass.REUSABLE

        self.add_node(DependencyNode(
            node_id="intermediate_gemm",
            operation="matmul_dot_products",
            estimated_cost=nominal_flops,
            memory_cost=M * N * 4,
            dependencies=["input_A", "input_B"],
            output_shape=(M, N),
            precision="float32",
            reuse_probability=0.5 if contract.cache_policy.value == "WARM" else 0.0,
            observability=1.0 if observable.output_type == "FULL_MATRIX" else 0.2,
            necessity=gemm_necessity,
            approximation_sensitivity=0.5
        ))
        self.add_edge("input_A", "intermediate_gemm")
        self.add_edge("input_B", "intermediate_gemm")

        # 4. Observable Node
        self.add_node(DependencyNode(
            node_id="observable_output",
            operation=f"observable_{observable.output_type.lower()}",
            estimated_cost=nominal_flops * observable.dimension_reduction_ratio,
            memory_cost=int(M * N * 4 * observable.dimension_reduction_ratio),
            dependencies=["intermediate_gemm"],
            output_shape=(M, N) if observable.output_type == "FULL_MATRIX" else (M, 1),
            precision="float32",
            reuse_probability=0.0,
            observability=1.0,
            necessity=NecessityClass.INDISPENSABLE,
            approximation_sensitivity=1.0,
            is_observable_target=True
        ))
        self.add_edge("intermediate_gemm", "observable_output")

        # Run backward pruning
        self.prune_unobserved_nodes(["observable_output"])

    def compute_summary(self) -> Dict[str, Any]:
        """Computes necessity statistics and work elimination potential."""
        total_nominal_cost = sum(n.estimated_cost for n in self.nodes.values())
        breakdown = {nc.value: 0 for nc in NecessityClass}
        for n in self.nodes.values():
            breakdown[n.necessity.value] += 1

        necessary_cost = sum(
            n.estimated_cost for n in self.nodes.values()
            if n.necessity in (NecessityClass.INDISPENSABLE, NecessityClass.CONDITIONALLY_REQUIRED)
        )
        work_elimination_potential = max(0.0, 1.0 - (necessary_cost / max(1.0, total_nominal_cost)))

        return {
            "graph_id": self.graph_id,
            "total_nodes": len(self.nodes),
            "total_nominal_cost_flops": total_nominal_cost,
            "necessary_cost_flops": necessary_cost,
            "work_elimination_potential": round(work_elimination_potential, 4),
            "classification_breakdown": breakdown
        }
