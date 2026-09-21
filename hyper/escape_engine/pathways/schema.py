"""
hyper/escape_engine/pathways/schema.py
======================================
Formal Representation of a Candidate Computational Pathway for VAEE.
Tracks structural, transformation, representation, and execution hashes to avoid superficial duplicates.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclasses.dataclass
class ComputationalPathway:
    pathway_id: str
    parent_id: Optional[str]
    workload_type: str
    transformation_chain: List[str]
    representation: str               # e.g., "DENSE", "CSR_SPARSE", "LOW_RANK_SVD", "STREAMING"
    execution_strategy: str           # "CPU_AVX2" | "IGPU_OPENCL" | "HYBRID_BALANCED" | "SCALAR"
    verification_strategy: str        # "EXACT_DIFFERENTIAL" | "FREIVALDS" | "INVARIANT"
    generation_depth: int = 0
    algorithm_family: str = "CANONICAL"
    parameters: Dict[str, Any] = dataclasses.field(default_factory=dict)
    
    # Callable compiled function or graph runner
    run_fn: Optional[Callable[..., Any]] = None

    @property
    def transformation_hash(self) -> str:
        """Hash of transformation sequence."""
        return hashlib.sha256("->".join(self.transformation_chain).encode()).hexdigest()[:16]

    @property
    def representation_hash(self) -> str:
        """Hash of the underlying representation."""
        return hashlib.sha256(self.representation.encode()).hexdigest()[:16]

    @property
    def execution_hash(self) -> str:
        """Hash of the execution strategy."""
        return hashlib.sha256(self.execution_strategy.encode()).hexdigest()[:16]

    @property
    def structural_hash(self) -> str:
        """
        Combined structural identity hash.
        Two pathways differ structurally only when their meaningful computational structure differs.
        """
        combined = f"{self.algorithm_family}:{self.representation}:{self.transformation_hash}:{self.execution_strategy}"
        return hashlib.sha256(combined.encode()).hexdigest()[:24]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pathway_id": self.pathway_id,
            "parent_id": self.parent_id,
            "workload_type": self.workload_type,
            "transformation_chain": self.transformation_chain,
            "representation": self.representation,
            "execution_strategy": self.execution_strategy,
            "verification_strategy": self.verification_strategy,
            "generation_depth": self.generation_depth,
            "algorithm_family": self.algorithm_family,
            "parameters": self.parameters,
            "structural_hash": self.structural_hash,
            "transformation_hash": self.transformation_hash,
        }
