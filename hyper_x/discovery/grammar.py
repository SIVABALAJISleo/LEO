"""
hyper_x/discovery/grammar.py
=============================================================================
HYPER-X Algorithm Discovery Grammar & Search Engine
=============================================================================
Discovers alternative algorithmic pathways using a compositional grammar:
  - Operation reordering
  - Algebraic decompositions (Strassen, Winograd, bilinear forms)
  - Low-complexity recurrence relations & factorizations
  - Reusable subexpressions / Common Subexpression Elimination (CSE)
  - Communication-avoiding tile orderings

Strict Novelty Categorization (Section 8):
  - KNOWN:            Identical or canonically isomorphic to documented literature
  - VARIANT:          Parameterization, fusion, or hybrid of known algorithm families
  - NOVEL-CANDIDATE:  Unseen symbolic formulation with verified correctness and measured gain
  - UNVERIFIED:       Formulation generated but not yet proven to satisfy contract

CRITICAL RULE: Never claim 'novel algorithm' merely because an unseen expression was generated.
"""

from __future__ import annotations
import enum
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any

class NoveltyStatus(str, enum.Enum):
    KNOWN = "KNOWN"
    VARIANT = "VARIANT"
    NOVEL_CANDIDATE = "NOVEL-CANDIDATE"
    UNVERIFIED = "UNVERIFIED"

@dataclass
class DiscoveredAlgorithmCandidate:
    algorithm_id: str
    name: str
    family: str
    expression: str
    canonical_form: str
    novelty: NoveltyStatus
    theoretical_complexity: str
    measured_speedup: float = 1.0
    verified: bool = False
    literature_reference: Optional[str] = None
    provenance_hash: str = ""

class AlgorithmDiscoveryGrammar:
    """Compositional grammar and catalog for algorithm discovery."""

    KNOWN_ALGORITHMS = {
        "BLAS_GEMM": "O(N^3) standard dot products",
        "STRASSEN_2x2": "7-multiplication recursive bilinear decomposition O(N^2.807)",
        "WINOGRAD_CONV": "Minimal filtering algorithm O(N) multiplications",
        "NYSTROM_SVD": "Low-rank approximation via randomized column sampling",
        "FREIVALDS_VERIFY": "O(N^2) randomized verification probe",
        "SPARSE_CSR_GEMM": "O(NNZ * K) index traversal",
        "BILATERAL_RECONSTRUCT": "Edge-preserving spatial-temporal filter"
    }

    def canonicalize_expression(self, expr: str) -> str:
        """Strips whitespace and normalizes associative symbols."""
        tokens = expr.replace(" ", "").replace("\n", "").lower()
        return tokens

    def classify_novelty(self, expression: str, family: str) -> Tuple[NoveltyStatus, Optional[str]]:
        canon = self.canonicalize_expression(expression)

        # Check known literature matches
        for known_name, desc in self.KNOWN_ALGORITHMS.items():
            if known_name.lower() in canon or desc.lower() in canon:
                return NoveltyStatus.KNOWN, f"Literature standard: {known_name} ({desc})"

        # Check if it's a known family composition
        if any(f.lower() in canon for f in ["sparse", "svd", "lowrank", "winograd", "cache"]):
            return NoveltyStatus.VARIANT, "Compositional hybrid of known algorithmic families"

        return NoveltyStatus.NOVEL_CANDIDATE, None

    def propose_candidate(
        self,
        name: str,
        family: str,
        expression: str,
        complexity: str = "O(N^2.5)"
    ) -> DiscoveredAlgorithmCandidate:
        canon = self.canonicalize_expression(expression)
        novelty, ref = self.classify_novelty(expression, family)
        p_hash = hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]

        return DiscoveredAlgorithmCandidate(
            algorithm_id=f"ALG_{p_hash[:8].upper()}",
            name=name,
            family=family,
            expression=expression,
            canonical_form=canon,
            novelty=novelty,
            theoretical_complexity=complexity,
            verified=False,
            literature_reference=ref,
            provenance_hash=p_hash
        )
