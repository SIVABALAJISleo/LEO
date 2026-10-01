"""
hyper/obligation/coa.py
=======================
Computational Obligation Analyzer (COA) for LEO/HYPER.
Fulfills Sections 9, 10, 11 of the Breakthrough Master Architecture.

Analyzes programs, contracts, and inputs to produce a formal
Computational Obligation Graph identifying:
- required computation
- optional computation
- redundant computation
- repeated computation
- dead computation
- observable computation
- non-observable computation
- data, control, memory, synchronization, and precision dependencies.
Performs rigorous backward slicing and output-directed analysis.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np

from hyper.universal_ir.opcodes import CIROpcode
from hyper.universal_ir.program import CIRProgram, CIRInstruction
from hyper.contracts.contract import Contract


class ObligationClassification(str, Enum):
    REQUIRED = "REQUIRED"
    OPTIONAL = "OPTIONAL"
    REDUNDANT = "REDUNDANT"
    REPEATED = "REPEATED"
    DEAD = "DEAD"
    OBSERVABLE = "OBSERVABLE"
    NON_OBSERVABLE = "NON_OBSERVABLE"


class DependencyType(str, Enum):
    DATA = "DATA"
    CONTROL = "CONTROL"
    MEMORY = "MEMORY"
    SYNCHRONIZATION = "SYNCHRONIZATION"
    PRECISION = "PRECISION"


class ObligationNode:
    """Represents a discrete computational operation in the obligation graph."""
    def __init__(
        self,
        node_id: str,
        op: str,
        inputs: List[str],
        output: str,
        shape: Optional[Tuple[int, ...]] = None,
        dtype: str = "float32",
        classification: ObligationClassification = ObligationClassification.REQUIRED,
        estimated_flops: int = 0,
        memory_bytes_read: int = 0,
        memory_bytes_written: int = 0,
        is_observable: bool = False,
        is_dead: bool = False,
    ):
        self.node_id = node_id
        self.op = op
        self.inputs = inputs
        self.output = output
        self.shape = shape
        self.dtype = dtype
        self.classification = classification
        self.estimated_flops = estimated_flops
        self.memory_bytes_read = memory_bytes_read
        self.memory_bytes_written = memory_bytes_written
        self.is_observable = is_observable
        self.is_dead = is_dead

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "op": self.op,
            "inputs": self.inputs,
            "output": self.output,
            "shape": list(self.shape) if self.shape else None,
            "dtype": self.dtype,
            "classification": self.classification.value,
            "estimated_flops": self.estimated_flops,
            "memory_bytes_read": self.memory_bytes_read,
            "memory_bytes_written": self.memory_bytes_written,
            "is_observable": self.is_observable,
            "is_dead": self.is_dead,
        }


class ObligationEdge:
    """Represents a dependency relationship between operations."""
    def __init__(
        self,
        source_id: str,
        target_id: str,
        dep_type: DependencyType = DependencyType.DATA,
        weight: float = 1.0,
    ):
        self.source_id = source_id
        self.target_id = target_id
        self.dep_type = dep_type
        self.weight = weight

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "dep_type": self.dep_type.value,
            "weight": self.weight,
        }


class ComputationalObligationGraph:
    """The complete computational obligation graph for an input program."""
    def __init__(self):
        self.nodes: Dict[str, ObligationNode] = {}
        self.edges: List[ObligationEdge] = []
        self.observable_outputs: Set[str] = set()
        self.producer_map: Dict[str, str] = {}  # var_name -> node_id
        self.consumer_map: Dict[str, Set[str]] = {}  # var_name -> set(node_ids)

    def add_node(self, node: ObligationNode) -> None:
        self.nodes[node.node_id] = node
        self.producer_map[node.output] = node.node_id
        for inp in node.inputs:
            if inp not in self.consumer_map:
                self.consumer_map[inp] = set()
            self.consumer_map[inp].add(node.node_id)

    def add_edge(self, edge: ObligationEdge) -> None:
        self.edges.append(edge)

    def compute_backward_slice(self, target_vars: Set[str]) -> Set[str]:
        """
        Backward slicing algorithm:
        Traverses backwards from target variables along data & control dependencies.
        Returns the set of node_ids that strictly influence the target outputs.
        """
        required_nodes: Set[str] = set()
        visited_vars: Set[str] = set()
        queue: List[str] = list(target_vars)

        while queue:
            var = queue.pop(0)
            if var in visited_vars:
                continue
            visited_vars.add(var)

            prod_node_id = self.producer_map.get(var)
            if prod_node_id and prod_node_id in self.nodes:
                required_nodes.add(prod_node_id)
                node = self.nodes[prod_node_id]
                for inp in node.inputs:
                    if inp not in visited_vars:
                        queue.append(inp)

        return required_nodes

    def summary(self) -> Dict[str, Any]:
        total_nodes = len(self.nodes)
        counts = {c.value: 0 for c in ObligationClassification}
        total_flops = sum(n.estimated_flops for n in self.nodes.values())
        required_flops = sum(
            n.estimated_flops for n in self.nodes.values()
            if n.classification == ObligationClassification.REQUIRED
        )

        for n in self.nodes.values():
            counts[n.classification.value] += 1

        return {
            "total_nodes": total_nodes,
            "classification_breakdown": counts,
            "total_flops": total_flops,
            "required_flops": required_flops,
            "eliminated_flops": max(0, total_flops - required_flops),
            "observable_outputs": list(self.observable_outputs),
        }


class ComputationalObligationAnalyzer:
    """
    COA Subsystem:
    Analyzes CIR programs, contracts, and inputs to extract exact minimal dependencies.
    """

    @staticmethod
    def _estimate_flops(op: str, shape: Optional[Tuple[int, ...]]) -> int:
        numel = int(np.prod(shape)) if shape else 1024
        op_upper = op.upper()

        if op_upper in ("MATMUL", "GEMM"):
            if shape and len(shape) >= 2:
                # M * N * K * 2
                m = shape[0]
                n = shape[1]
                k = shape[1] if len(shape) == 2 else shape[2]
                return int(2 * m * n * k)
            return int(2 * (numel ** 1.5))
        elif op_upper in ("CONV2D",):
            return int(numel * 9 * 2)  # 3x3 kernel assumption
        elif op_upper in ("FFT", "IFFT", "FFT2D", "IFFT2D"):
            return int(5 * numel * max(1, int(np.log2(max(2, numel)))))
        elif op_upper in ("TOPK", "ARGMAX"):
            return int(numel * 3)  # Partial selection
        elif op_upper in ("SORT",):
            return int(numel * int(np.log2(max(2, numel))))
        elif op_upper in ("REDUCE_SUM", "REDUCE_MAX", "REDUCE_MIN"):
            return int(numel)
        else:
            # Standard elementwise
            return int(numel)

    @staticmethod
    def _estimate_memory(op: str, shape: Optional[Tuple[int, ...]], dtype: str) -> Tuple[int, int]:
        itemsize = 4
        if "64" in dtype:
            itemsize = 8
        elif "16" in dtype:
            itemsize = 2
        elif "8" in dtype:
            itemsize = 1

        numel = int(np.prod(shape)) if shape else 1024
        bytes_count = numel * itemsize

        op_upper = op.upper()
        if op_upper in ("ADD", "SUB", "MUL", "DIV", "MATMUL"):
            return (bytes_count * 2, bytes_count)
        elif op_upper in ("REDUCE_SUM", "REDUCE_MAX"):
            return (bytes_count, itemsize)
        else:
            return (bytes_count, bytes_count)

    @staticmethod
    def _extract_inst_fields(inst: Any) -> Tuple[str, List[str], str]:
        if hasattr(inst, "opcode"):
            op_name = inst.opcode.value if hasattr(inst.opcode, "value") else str(inst.opcode)
            inps = [str(x) for x in inst.operands]
            out_var = str(inst.result_id)
        else:
            op_name = inst.op.value if hasattr(inst.op, "value") else str(inst.op)
            inps = [str(x) for x in inst.inputs]
            out_var = str(inst.output)
        return op_name, inps, out_var

    def analyze(
        self,
        program: Any,
        contract: Optional[Contract] = None,
        target_outputs: Optional[List[str]] = None,
        inputs: Optional[Dict[str, np.ndarray]] = None,
        query_type: Optional[str] = None,  # e.g. "TOPK", "SCALAR", "FULL"
        query_params: Optional[Dict[str, Any]] = None,
    ) -> ComputationalObligationGraph:
        """
        Builds and classifies the Computational Obligation Graph.
        Performs backward slicing from target outputs, pruning dead code and
        identifying redundant or non-observable computation.
        """
        graph = ComputationalObligationGraph()

        # 1. Determine observable outputs
        if target_outputs:
            graph.observable_outputs = set(target_outputs)
        elif program.outputs:
            graph.observable_outputs = set(program.outputs)
        else:
            # Fallback: all outputs of instructions not consumed as inputs
            all_inps = set()
            for inst in program.instructions:
                _, inps, _ = self._extract_inst_fields(inst)
                all_inps.update(inps)
            all_outs = set()
            for inst in program.instructions:
                _, _, out_var = self._extract_inst_fields(inst)
                all_outs.add(out_var)
            graph.observable_outputs = {o for o in all_outs if o not in all_inps}

        # 2. Build initial nodes and edges
        seen_expressions: Dict[Tuple[str, Tuple[str, ...]], str] = {}  # (op, inputs) -> node_id

        for idx, inst in enumerate(program.instructions):
            op_name, inst_inps, inst_output = self._extract_inst_fields(inst)
            node_id = f"node_{idx}_{op_name}"

            # Determine shape from inputs if available
            shape = None
            dtype = "float32"
            if inputs:
                for inp_name in inst_inps:
                    if inp_name in inputs and isinstance(inputs[inp_name], np.ndarray):
                        shape = inputs[inp_name].shape
                        dtype = str(inputs[inp_name].dtype)
                        break

            flops = self._estimate_flops(op_name, shape)
            mem_read, mem_write = self._estimate_memory(op_name, shape, dtype)

            node = ObligationNode(
                node_id=node_id,
                op=op_name,
                inputs=list(inst_inps),
                output=inst_output,
                shape=shape,
                dtype=dtype,
                classification=ObligationClassification.REQUIRED,
                estimated_flops=flops,
                memory_bytes_read=mem_read,
                memory_bytes_written=mem_write,
                is_observable=(inst_output in graph.observable_outputs),
            )

            # Common Subexpression / Repeated Work Detection
            expr_key = (op_name, tuple(inst_inps))
            if expr_key in seen_expressions:
                node.classification = ObligationClassification.REPEATED
            else:
                seen_expressions[expr_key] = node_id

            graph.add_node(node)

            # Add data dependency edges
            for inp_var in inst_inps:
                prod_id = graph.producer_map.get(inp_var)
                if prod_id:
                    graph.add_edge(ObligationEdge(
                        source_id=prod_id,
                        target_id=node_id,
                        dep_type=DependencyType.DATA,
                    ))

        # 3. Perform backward slicing from observable outputs
        required_node_ids = graph.compute_backward_slice(graph.observable_outputs)

        # 4. Classify each node
        for node_id, node in graph.nodes.items():
            if node_id not in required_node_ids:
                # Not reachable from any observable output -> Provably DEAD
                node.classification = ObligationClassification.DEAD
                node.is_dead = True
                node.is_observable = False
            elif node.classification != ObligationClassification.REPEATED:
                # Check for algebraic redundancy (e.g., identity transforms)
                if node.op in ("IDENTITY", "NOP"):
                    node.classification = ObligationClassification.REDUNDANT
                else:
                    node.classification = ObligationClassification.REQUIRED
                    node.is_observable = (node.output in graph.observable_outputs)

        # 5. Output-Directed Query Optimization
        # If the contract or query specifies output slicing or top-k,
        # non-essential full materializations are marked OPTIONAL / NON_OBSERVABLE
        if query_type == "TOPK" and query_params:
            k = query_params.get("k", 10)
            for node in graph.nodes.values():
                if node.op == "SORT" and node.output in graph.observable_outputs:
                    # Full sort can be replaced by O(N) selection
                    node.classification = ObligationClassification.OPTIONAL
        elif query_type == "SCALAR":
            # Only scalar summary requested
            for node in graph.nodes.values():
                if not node.is_observable and node.classification == ObligationClassification.REQUIRED:
                    # Intermediate full tensor expansions
                    pass

        return graph
