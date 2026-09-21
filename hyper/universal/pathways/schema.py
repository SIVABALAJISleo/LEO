"""
hyper/universal/pathways/schema.py
==================================
Formal representation of candidate computational pathways.
"""

from __future__ import annotations

import dataclasses
import hashlib
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class TransformationFamily(str, Enum):
    MATHEMATICAL = "MATHEMATICAL"               # 7.1: Factorization, algebraic identities, CSE
    ALGORITHMIC = "ALGORITHMIC"                 # 7.2: Divide & conquer, DP, greedy, graph rewrites
    STRUCTURAL = "STRUCTURAL"                   # 7.3: Sparsity, low-rank SVD, symmetry, separability
    REPRESENTATION = "REPRESENTATION"           # 7.4: Dense, sparse CSR, quantized int8/ternary, packed
    INCREMENTAL = "INCREMENTAL"                 # 7.5: Memoization, delta, prefix/suffix reuse
    OUTPUT_DIRECTED = "OUTPUT_DIRECTED"         # 7.6: Compute only genuinely needed output elements
    MEMORY = "MEMORY"                           # 7.7: Cache tiling, buffer recycling, memory layout
    SCHEDULING = "SCHEDULING"                   # 7.8: CPU AVX2, iGPU OpenCL, CPU+iGPU co-execution
    COMPILER = "COMPILER"                       # 7.9: Vectorization, strength reduction, loop unroll
    PROGRAM_SYNTHESIS = "PROGRAM_SYNTHESIS"     # 7.10: Synthesized AST code within sandboxed limits


@dataclasses.dataclass
class UniversalPathway:
    pathway_id: str
    family: TransformationFamily
    name: str
    transformation_chain: List[str]
    structural_hash: str
    parent_id: Optional[str] = None
    target_hardware: str = "CPU_AVX2"           # "CPU_AVX2" | "INTEL_UHD_IGPU" | "CPU_IGPU_COEXEC"
    run_fn: Optional[Callable[[Any], Any]] = None
    synthesized_code: Optional[str] = None
    lineage_depth: int = 0
    estimated_speedup: float = 1.0
    metadata: Dict[str, Any] = dataclasses.field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pathway_id": self.pathway_id,
            "family": self.family.value,
            "name": self.name,
            "transformation_chain": self.transformation_chain,
            "structural_hash": self.structural_hash,
            "parent_id": self.parent_id,
            "target_hardware": self.target_hardware,
            "lineage_depth": self.lineage_depth,
            "estimated_speedup": self.estimated_speedup,
            "has_synthesized_code": self.synthesized_code is not None,
            "metadata": self.metadata,
        }

    @staticmethod
    def compute_structural_hash(family: str, transformations: List[str], hardware: str, code_snippet: Optional[str] = None) -> str:
        h = hashlib.sha256()
        h.update(family.encode("utf-8"))
        h.update(hardware.encode("utf-8"))
        for t in transformations:
            h.update(t.encode("utf-8"))
        if code_snippet:
            # Strip whitespace to ensure semantic hashing
            normalized = "".join(code_snippet.split())
            h.update(normalized.encode("utf-8"))
        return h.hexdigest()[:16]
