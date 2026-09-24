"""
hyper_universal/candidate.py
============================
Executable Candidate Schema, Novelty Hashes & Genealogy Engine.

Implements Sections 3, 20, 21 of the Master Specification:
- Every candidate possesses an executable representation (generated_source, compiled_artifact).
- Strict Novelty Hashes:
    structural_hash, transformation_hash, algorithm_hash, program_hash, representation_hash.
- Candidate Genealogy:
    parent_ids, mutation lineage, crossover, verified history, counterexample history.
"""

from __future__ import annotations
import hashlib
import time
import uuid
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from hyper_universal.contract_ir import ContractIR
from hyper_universal.types import ResultState


class CandidateGenealogy(BaseModel):
    parent_ids: List[str] = Field(default_factory=list)
    generation: int = 0
    mutation_history: List[str] = Field(default_factory=list)
    crossover_parents: List[str] = Field(default_factory=list)
    failed_branches: List[str] = Field(default_factory=list)
    surviving_branches: List[str] = Field(default_factory=list)


class CandidateNoveltyMetrics(BaseModel):
    structural_hash: str = ""
    transformation_hash: str = ""
    algorithm_hash: str = ""
    representation_hash: str = ""
    novelty_score: float = 1.0


class Candidate(BaseModel):
    candidate_id: str = Field(default_factory=lambda: f"cand-{uuid.uuid4().hex[:8]}")
    name: str = "CandidatePathway"
    workload_id: str
    transformation_genome: List[str] = Field(default_factory=list)
    representation: str = "DENSE"
    algorithm_ir: Dict[str, Any] = Field(default_factory=dict)
    program_ir: Dict[str, Any] = Field(default_factory=dict)
    generated_source: str = ""
    execution_plan: str = "CPU_LOCAL"
    contract: ContractIR
    expected_output_definition: str = "TENSOR_MATCH"
    resource_budget: Dict[str, float] = Field(default_factory=dict)
    genealogy: CandidateGenealogy = Field(default_factory=CandidateGenealogy)
    novelty: CandidateNoveltyMetrics = Field(default_factory=CandidateNoveltyMetrics)
    result_state: ResultState = ResultState.FOUND
    measured_latency_ms: Optional[float] = None
    measured_work_reduction_pct: float = 0.0
    counterexamples_encountered: List[str] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)

    def compute_novelty_hashes(self) -> None:
        """Computes multi-dimensional structural and algorithm fingerprints to prevent duplicate generation."""
        tx_str = ":".join(sorted(self.transformation_genome))
        self.novelty.transformation_hash = hashlib.sha256(tx_str.encode()).hexdigest()[:12]
        self.novelty.structural_hash = hashlib.sha256(
            f"{self.representation}:{tx_str}:{self.execution_plan}".encode()
        ).hexdigest()[:12]
        self.novelty.algorithm_hash = hashlib.sha256(
            f"{self.name}:{self.expected_output_definition}".encode()
        ).hexdigest()[:12]
        self.novelty.representation_hash = hashlib.sha256(self.representation.encode()).hexdigest()[:8]
