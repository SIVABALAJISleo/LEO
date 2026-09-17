"""
hyper/v8/nwc.py
===============
HYPER v8 — Necessary-Work Compiler (NWC).

Core question: "What portion of the reference computation is causally
necessary for this exact input and this exact application contract?"

Components:
    NecessityLabel          - per-node labels: REQUIRED/OPTIONAL/REUSABLE/...
    NecessaryWorkMap        - maps op nodes to necessity labels
    NecessaryWorkGraph      - DAG of operations with dependency/cost/device info
    DependencyAnalyzer      - maps output elements to causally required inputs
    ChangeDetectionEngine   - classifies deltas: UNCHANGED/DEPENDENT/INDEPENDENT
    NWCMetrics              - NWR (Necessary Work Ratio) and EWR metrics

Scientific rules:
    - NWR = necessary_work / reference_work (theoretical)
    - MRR = measured_runtime_reduction (must be measured separately)
    - Never confuse theoretical NWR with measured MRR.
"""

from __future__ import annotations

import dataclasses
import enum
import hashlib
import time
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# NECESSITY LABEL
# ─────────────────────────────────────────────────────────────────────────────

class NecessityLabel(enum.Enum):
    REQUIRED      = "REQUIRED"       # must be computed for this contract
    OPTIONAL      = "OPTIONAL"       # output not required by contract
    REUSABLE      = "REUSABLE"       # can be replayed from cache
    ELIMINABLE    = "ELIMINABLE"     # provably unreachable by input change
    APPROXIMABLE  = "APPROXIMABLE"   # can be approximated within contract
    UNKNOWN       = "UNKNOWN"        # cannot determine necessity


class ChangeLabel(enum.Enum):
    UNCHANGED   = "UNCHANGED"    # input is identical to previous
    DEPENDENT   = "DEPENDENT"    # output depends on changed inputs
    INDEPENDENT = "INDEPENDENT"  # output provably independent of change
    UNKNOWN     = "UNKNOWN"      # cannot determine


# ─────────────────────────────────────────────────────────────────────────────
# OPERATION NODE
# ─────────────────────────────────────────────────────────────────────────────

@dataclasses.dataclass
class OpNode:
    """A single node in the NecessaryWorkGraph."""
    node_id: str
    op_name: str
    input_ids: List[str]          # upstream node IDs
    output_shape: Optional[tuple] = None
    estimated_flops: int = 0
    device: str = "CPU"           # CPU | INTEL_UHD | HYBRID
    reuse_count: int = 0          # how many times this has been reused
    necessity: NecessityLabel = NecessityLabel.UNKNOWN
    change_status: ChangeLabel = ChangeLabel.UNKNOWN
    last_output_digest: Optional[str] = None
    metadata: Dict[str, Any] = dataclasses.field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# NECESSARY WORK MAP
# ─────────────────────────────────────────────────────────────────────────────

@dataclasses.dataclass
class NecessaryWorkMap:
    """Per-node necessity labels for a computation graph."""
    nodes: Dict[str, OpNode] = dataclasses.field(default_factory=dict)

    def label(self, node_id: str, label: NecessityLabel) -> None:
        if node_id in self.nodes:
            self.nodes[node_id].necessity = label

    def get_label(self, node_id: str) -> NecessityLabel:
        node = self.nodes.get(node_id)
        return node.necessity if node else NecessityLabel.UNKNOWN

    def eliminable_nodes(self) -> List[str]:
        return [nid for nid, n in self.nodes.items()
                if n.necessity == NecessityLabel.ELIMINABLE]

    def required_nodes(self) -> List[str]:
        return [nid for nid, n in self.nodes.items()
                if n.necessity == NecessityLabel.REQUIRED]

    def necessary_work_ratio(self) -> Tuple[float, float]:
        """
        Returns (NWR, EWR) where:
          NWR = required_flops / total_flops  (fraction needed)
          EWR = 1 - NWR                        (fraction eliminated)

        NOTE: This is theoretical FLOP ratio, NOT measured runtime.
        """
        total = sum(n.estimated_flops for n in self.nodes.values())
        required = sum(
            n.estimated_flops for n in self.nodes.values()
            if n.necessity == NecessityLabel.REQUIRED
        )
        if total == 0:
            return 1.0, 0.0
        nwr = required / total
        return nwr, 1.0 - nwr

    def summary(self) -> Dict[str, Any]:
        counts = {}
        for label in NecessityLabel:
            counts[label.value] = sum(
                1 for n in self.nodes.values() if n.necessity == label
            )
        nwr, ewr = self.necessary_work_ratio()
        return {
            "node_counts": counts,
            "total_nodes": len(self.nodes),
            "nwr_theoretical": round(nwr, 4),
            "ewr_theoretical": round(ewr, 4),
            "warning": "NWR is theoretical FLOP ratio. Measure MRR separately.",
        }


# ─────────────────────────────────────────────────────────────────────────────
# NECESSARY WORK GRAPH
# ─────────────────────────────────────────────────────────────────────────────

class NecessaryWorkGraph:
    """
    DAG of operations. Each node carries: op, deps, cost, device, reuse, contract_impact.

    Supports:
        - node elimination (dead-work removal)
        - node reuse (cache insertion)
        - node fusion (producer-consumer)
        - node substitution (cheaper equivalent)
        - necessity propagation (backward from output)
    """

    def __init__(self) -> None:
        self.nodes: Dict[str, OpNode] = {}
        self._output_ids: Set[str] = set()

    def add_node(self, node: OpNode) -> None:
        self.nodes[node.node_id] = node

    def mark_output(self, node_id: str) -> None:
        self._output_ids.add(node_id)

    def build_necessity_map(self) -> NecessaryWorkMap:
        """
        Backward pass from output nodes.
        Any node reachable from an output is REQUIRED (unless proven independent).
        Unreachable nodes are ELIMINABLE.
        """
        nwm = NecessaryWorkMap(nodes=dict(self.nodes))
        required: Set[str] = set()

        def _mark_required(nid: str) -> None:
            if nid in required:
                return
            required.add(nid)
            node = self.nodes.get(nid)
            if node:
                for inp in node.input_ids:
                    _mark_required(inp)

        for oid in self._output_ids:
            _mark_required(oid)

        for nid, node in nwm.nodes.items():
            if nid in required:
                if node.change_status == ChangeLabel.UNCHANGED and node.last_output_digest:
                    node.necessity = NecessityLabel.REUSABLE
                else:
                    node.necessity = NecessityLabel.REQUIRED
            else:
                node.necessity = NecessityLabel.ELIMINABLE

        return nwm

    def topological_order(self) -> List[str]:
        """Kahn's algorithm."""
        in_degree: Dict[str, int] = {nid: 0 for nid in self.nodes}
        children: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for nid, node in self.nodes.items():
            for inp in node.input_ids:
                if inp in children:
                    children[inp].append(nid)
                    in_degree[nid] += 1

        queue = [nid for nid, d in in_degree.items() if d == 0]
        order = []
        while queue:
            nid = queue.pop(0)
            order.append(nid)
            for child in children[nid]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)
        return order

    def total_estimated_flops(self) -> int:
        return sum(n.estimated_flops for n in self.nodes.values())


# ─────────────────────────────────────────────────────────────────────────────
# DEPENDENCY ANALYZER
# ─────────────────────────────────────────────────────────────────────────────

class DependencyAnalyzer:
    """
    Maps output elements to the input elements that can causally affect them.

    For matrix multiplication C = A @ B:
        C[i,j] depends on A[i,:] and B[:,j]

    This allows the NWC to determine which outputs need recomputing
    when only a subset of inputs change.
    """

    @staticmethod
    def analyze_matmul(
        a_changed_rows: Optional[Set[int]],
        b_changed_cols: Optional[Set[int]],
        m: int, k: int, n: int,
    ) -> Dict[str, Any]:
        """
        For C = A @ B (m×k × k×n → m×n):
          If only rows i∈S of A changed: only rows i of C are affected.
          If only cols j∈T of B changed: only cols j of C are affected.
          If both: union of affected rows/cols.
        """
        if a_changed_rows is None and b_changed_cols is None:
            return {"affected_rows": None, "affected_cols": None,
                    "fraction_affected": 1.0, "analysis": "FULL_RECOMPUTE"}

        affected_rows = a_changed_rows  # C rows follow A rows
        affected_cols = b_changed_cols  # C cols follow B cols

        if affected_rows is not None and affected_cols is not None:
            fraction = len(affected_rows) / m + len(affected_cols) / n
        elif affected_rows is not None:
            fraction = len(affected_rows) / m
        elif affected_cols is not None:
            fraction = len(affected_cols) / n
        else:
            fraction = 0.0

        return {
            "affected_rows": sorted(affected_rows) if affected_rows else None,
            "affected_cols": sorted(affected_cols) if affected_cols else None,
            "fraction_affected": min(1.0, fraction),
            "analysis": "PARTIAL_RECOMPUTE" if fraction < 1.0 else "FULL_RECOMPUTE",
        }

    @staticmethod
    def analyze_elementwise(
        changed_mask: np.ndarray,
    ) -> Dict[str, Any]:
        """
        For elementwise ops: output[i] depends only on input[i].
        Only changed positions need recomputing.
        """
        n_changed = int(np.sum(changed_mask))
        n_total = changed_mask.size
        return {
            "n_changed": n_changed,
            "n_total": n_total,
            "fraction_affected": n_changed / max(1, n_total),
            "analysis": "ELEMENTWISE_PARTIAL" if n_changed < n_total else "FULL_RECOMPUTE",
        }


# ─────────────────────────────────────────────────────────────────────────────
# CHANGE DETECTION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class ChangeDetectionEngine:
    """
    Detects what changed between two computational states.

    Uses cryptographic hashing for exact identity.
    Uses structural analysis for partial-change detection.

    Output classification per region:
        UNCHANGED   - bit-identical to previous
        DEPENDENT   - may have changed (must recompute)
        INDEPENDENT - provably unaffected by any change
        UNKNOWN     - cannot determine
    """

    def __init__(self) -> None:
        self._previous_digests: Dict[str, str] = {}

    def _digest(self, arr: np.ndarray) -> str:
        h = hashlib.sha256()
        h.update(arr.tobytes())
        h.update(str(arr.shape).encode())
        h.update(str(arr.dtype).encode())
        return h.hexdigest()

    def classify(
        self,
        current: np.ndarray,
        tensor_id: str,
    ) -> ChangeLabel:
        """Compare current tensor to stored previous state."""
        digest = self._digest(current)
        prev = self._previous_digests.get(tensor_id)
        self._previous_digests[tensor_id] = digest

        if prev is None:
            return ChangeLabel.UNKNOWN   # first time — no prior state
        if digest == prev:
            return ChangeLabel.UNCHANGED
        return ChangeLabel.DEPENDENT

    def changed_rows(
        self,
        prev: np.ndarray,
        current: np.ndarray,
    ) -> Optional[Set[int]]:
        """Return set of row indices that changed. None = all changed."""
        if prev.shape != current.shape:
            return None
        changed = set()
        for i in range(prev.shape[0]):
            if not np.array_equal(prev[i], current[i]):
                changed.add(i)
        return changed if len(changed) < prev.shape[0] else None

    def changed_cols(
        self,
        prev: np.ndarray,
        current: np.ndarray,
    ) -> Optional[Set[int]]:
        """Return set of column indices that changed. None = all changed."""
        if prev.shape != current.shape:
            return None
        changed = set()
        for j in range(prev.shape[1]):
            if not np.array_equal(prev[:, j], current[:, j]):
                changed.add(j)
        return changed if len(changed) < prev.shape[1] else None

    def change_fraction(self, prev: np.ndarray, current: np.ndarray) -> float:
        """Element-wise fraction of changed values."""
        if prev.shape != current.shape:
            return 1.0
        n_changed = int(np.sum(prev != current))
        return n_changed / max(1, prev.size)


# ─────────────────────────────────────────────────────────────────────────────
# NWC METRICS
# ─────────────────────────────────────────────────────────────────────────────

@dataclasses.dataclass
class NWCMetrics:
    """
    Separate theoretical and measured metrics. NEVER mix them.

    NWR = necessary_work / reference_work     (theoretical FLOP ratio)
    EWR = 1 - NWR                              (theoretical eliminated fraction)
    MRR = measured_runtime_reduction           (wall-clock, always measured)
    CER = reference_cost / accepted_path_cost  (measured)
    """
    # Theoretical
    nwr_theoretical: float = 1.0
    ewr_theoretical: float = 0.0

    # Measured (from perf_counter_ns)
    reference_time_ms: float = 0.0
    optimized_time_ms: float = 0.0
    mrr_measured: float = 0.0       # runtime reduction fraction
    cer_measured: float = 1.0       # speedup ratio

    # Verification
    max_abs_error: float = 0.0
    contract_passed: bool = False

    def __post_init__(self) -> None:
        if self.reference_time_ms > 0:
            self.mrr_measured = max(
                0.0, 1.0 - self.optimized_time_ms / self.reference_time_ms
            )
            self.cer_measured = self.reference_time_ms / max(
                1e-6, self.optimized_time_ms
            )

    def report(self) -> Dict[str, Any]:
        return {
            "nwr_theoretical": f"{self.nwr_theoretical:.4f}",
            "ewr_theoretical": f"{self.ewr_theoretical:.4f}",
            "reference_time_ms": f"{self.reference_time_ms:.3f}",
            "optimized_time_ms": f"{self.optimized_time_ms:.3f}",
            "mrr_measured": f"{self.mrr_measured:.4f}",
            "cer_measured": f"{self.cer_measured:.2f}x",
            "max_abs_error": f"{self.max_abs_error:.3e}",
            "contract_passed": self.contract_passed,
            "WARNING": "NWR/EWR are theoretical. MRR/CER are measured wall-clock.",
        }
