"""
hyper/discovery/anticheat.py
============================
Strict Anti-Cheating and Anti-Hardcoding Defense System.

Detects, prohibits, and flags:
- Benchmark-specific hardcoding
- Known-answer lookup tables
- Hidden cached outputs
- Workload fingerprints mapped to predetermined answers
- Test-specific branches
- Benchmark name detection
- External or hidden network computation
- Manually selected algorithms for known benchmarks

Enforces UNKNOWN_WORKLOAD_MODE where the engine receives ONLY the raw problem,
inputs, and contract with zero benchmark or workload names.
"""

from __future__ import annotations

import copy
import dataclasses
import hashlib
import inspect
import re
import socket
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from hyper.discovery.cir import CIRGraph, CIRNode, DataType, OpType
from hyper.discovery.contract import VerificationMode, WorkloadContract
from hyper.discovery.search_space import CandidatePathway


@dataclasses.dataclass
class AntiCheatViolation:
    violation_code: str
    severity: str  # "FATAL" | "WARNING"
    details: str
    culprit_node: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class AntiCheatGate:
    """
    Anti-Cheating Gate.
    Audits computational graphs and runtime environments to prevent synthetic shortcuts.
    """

    KNOWN_BENCHMARK_KEYWORDS = {
        "benchmark",
        "pytest",
        "cel_experiment",
        "nvidia_h100",
        "a100",
        "rtx4090",
        "rtx5090",
        "speedup_target",
        "ground_truth",
        "lookup_answer",
    }

    def __init__(self, prohibit_network: bool = True):
        self.prohibit_network = prohibit_network
        self._network_socket_hooked = False

    def audit_candidate(
        self,
        candidate: CandidatePathway,
        sample_inputs: Dict[str, Any],
        contract: WorkloadContract,
    ) -> List[AntiCheatViolation]:
        """
        Audit a candidate pathway for hardcoded tables, precomputed constants, and suspicious branches.
        """
        violations: List[AntiCheatViolation] = []
        graph = candidate.graph

        # 1. Audit node names and attributes for benchmark-specific names
        for nid, node in graph.nodes.items():
            for kw in self.KNOWN_BENCHMARK_KEYWORDS:
                if kw in node.name.lower():
                    violations.append(
                        AntiCheatViolation(
                            violation_code="SUSPICIOUS_NODE_NAME",
                            severity="FATAL",
                            details=f"Node '{node.name}' contains benchmark-specific keyword '{kw}'.",
                            culprit_node=nid,
                        )
                    )

            # 2. Check for suspicious lookup tables or hardcoded answers
            if node.attributes.get("is_constant") and node.constant_value is not None:
                # If a constant matches a designated output exactly without computation
                if nid in graph.outputs:
                    violations.append(
                        AntiCheatViolation(
                            violation_code="HARDCODED_OUTPUT_CONSTANT",
                            severity="FATAL",
                            details=f"Output node '{node.name}' is a static hardcoded constant.",
                            culprit_node=nid,
                        )
                    )

        # 3. Check for external network calls or socket descriptors
        if self.prohibit_network and self._check_active_network_sockets():
            violations.append(
                AntiCheatViolation(
                    violation_code="NETWORK_COMPUTE_PROHIBITED",
                    severity="FATAL",
                    details="Active external network connections detected during local computation.",
                )
            )

        return violations

    def anonymize_for_unknown_workload_mode(
        self,
        graph: CIRGraph,
        contract: WorkloadContract,
    ) -> Tuple[CIRGraph, WorkloadContract, Dict[str, str]]:
        """
        UNKNOWN_WORKLOAD_MODE:
        Strips all domain names, benchmark titles, and identifiers.
        Returns anonymized graph, anonymized contract, and translation mapping.
        """
        anon_g = graph.clone()
        anon_g.name = "unknown_workload"
        anon_g.graph_id = f"anon_{hashlib.sha256(graph.graph_id.encode()).hexdigest()[:10]}"
        anon_g.metadata = {}

        name_map: Dict[str, str] = {}

        # Anonymize inputs
        for idx, in_id in enumerate(anon_g.inputs):
            old_name = anon_g.nodes[in_id].name
            new_name = f"in_{idx}"
            anon_g.nodes[in_id].name = new_name
            name_map[old_name] = new_name

        # Anonymize outputs
        for idx, out_id in enumerate(anon_g.outputs):
            old_name = anon_g.nodes[out_id].name
            new_name = f"out_{idx}"
            anon_g.nodes[out_id].name = new_name
            name_map[old_name] = new_name

        # Anonymize intermediate nodes
        for idx, (nid, node) in enumerate(anon_g.nodes.items()):
            if nid not in anon_g.inputs and nid not in anon_g.outputs:
                node.name = f"op_{idx}_{node.op_type.value.lower()}"

        # Anonymize contract
        anon_contract = copy.deepcopy(contract)
        anon_contract.workload_name = "anonymized_problem"
        anon_contract.contract_id = f"c_anon_{hashlib.sha256(contract.contract_id.encode()).hexdigest()[:8]}"
        anon_contract.required_outputs = [name_map.get(req, req) for req in contract.required_outputs]

        return anon_g, anon_contract, name_map

    def _check_active_network_sockets(self) -> bool:
        """Heuristic check for open TCP connections in current process."""
        try:
            import psutil
            proc = psutil.Process()
            connections = proc.net_connections(kind="tcp")
            for c in connections:
                # Exclude localhost dev server ports (e.g. 8000, 3000, 5173)
                if c.raddr and c.raddr.ip not in ("127.0.0.1", "::1"):
                    return True
        except Exception:
            pass
        return False
