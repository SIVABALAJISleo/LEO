"""
hyper/hyper100_parity/score_engine.py
=====================================
100% Parity Score Engine & Global Coverage Matrix (Sections 30, 31, 46).

Implements:
1. Formal Capability Multi-Dimensional Parity Score (Section 30):
   Evaluates all 9 dimensions:
   - FunctionalParity (0.0 to 100.0%)
   - ComputationalParity (0.0 to 100.0%)
   - ContractParity (0.0 to 100.0%)
   - QualityParity (0.0 to 100.0%)
   - PerformanceContractParity (0.0 to 100.0%)
   - ApplicationParity (0.0 to 100.0%)
   - EdgeCaseParity (0.0 to 100.0%)
   - AdversarialParity (0.0 to 100.0%)
   - ReproducibilityParity (0.0 to 100.0%)

   Iron Rule:
     A capability is 100% VERIFIED ONLY when every required dimension passes.
     Do NOT average unrelated dimensions and call the average "100%".

2. Global 100% Score & Coverage Matrix (Section 31):
   GlobalParity = VerifiedCapabilities / RequiredCapabilities
   Separately reports:
   - Exact coverage
   - Contract coverage
   - Application coverage
   - Performance-contract coverage
   - Adversarial coverage
   Never hides weak categories inside an average.

3. Required Pathway Report (Section 46):
   Emits formal comprehensive `pathway_report` matching the specification.
"""

from __future__ import annotations
import json
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .taxonomy import CapabilityFamily, EquivalenceClass, EvidenceLevel


class CapabilityParityScore(BaseModel):
    capability_id: str
    workload_name: str
    family: CapabilityFamily

    functional_parity_pct: float = 0.0
    computational_parity_pct: float = 0.0
    contract_parity_pct: float = 0.0
    quality_parity_pct: float = 0.0
    performance_contract_parity_pct: float = 0.0
    application_parity_pct: float = 0.0
    edge_case_parity_pct: float = 0.0
    adversarial_parity_pct: float = 0.0
    reproducibility_parity_pct: float = 0.0

    is_100_percent_verified: bool = False
    evidence_level: EvidenceLevel = EvidenceLevel.MEASURED

    def evaluate_100_percent_status(self) -> bool:
        """A capability is 100% VERIFIED only when all 9 dimensions reach 100.0%."""
        all_passed = (
            self.functional_parity_pct >= 100.0
            and self.computational_parity_pct >= 100.0
            and self.contract_parity_pct >= 100.0
            and self.quality_parity_pct >= 100.0
            and self.performance_contract_parity_pct >= 100.0
            and self.application_parity_pct >= 100.0
            and self.edge_case_parity_pct >= 100.0
            and self.adversarial_parity_pct >= 100.0
            and self.reproducibility_parity_pct >= 100.0
        )
        self.is_100_percent_verified = all_passed
        return all_passed


class GlobalCoverageMatrix(BaseModel):
    total_required_capabilities: int
    verified_capabilities_count: int
    global_verified_parity_pct: float

    exact_coverage_pct: float
    contract_coverage_pct: float
    application_coverage_pct: float
    performance_contract_coverage_pct: float
    adversarial_coverage_pct: float
    blind_holdout_coverage_pct: float

    category_coverage: Dict[str, float] = Field(default_factory=dict)
    capability_scores: List[CapabilityParityScore] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)


class PathwayReport(BaseModel):
    """
    Formal comprehensive report matching Section 46 specifications.
    """
    pathway_id: str
    capability: str
    workload: str
    original_algorithm: str
    discovered_algorithm: str
    transformations: List[str]
    mathematical_basis: str
    contract: str
    equivalence_class: str
    certificate: str
    reference_result: str
    candidate_result: str
    exactness: str
    numerical_error: float
    quality: float
    latency: Dict[str, float]  # reference_ms, candidate_ms
    throughput: float
    memory: Dict[str, float]
    cpu_usage: float
    igpu_usage: float
    temperature: float
    power: float
    work_reduction: float
    reuse: float
    reconstruction: float
    fallback: float
    adversarial_results: str
    blind_holdout_results: str
    reproducibility: str
    evidence_level: str
    parity_percentage: float
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ParityScoreEngine:
    """
    Computes rigorous unembellished coverage matrices and formal Section 46 reports.
    """

    @staticmethod
    def calculate_global_matrix(scores: List[CapabilityParityScore], holdout_score: float = 1.0) -> GlobalCoverageMatrix:
        total = max(len(scores), 1)
        verified = sum(1 for s in scores if s.evaluate_100_percent_status())

        exact_cov = sum(1 for s in scores if s.computational_parity_pct >= 100.0) / total * 100.0
        ctr_cov = sum(1 for s in scores if s.contract_parity_pct >= 100.0) / total * 100.0
        app_cov = sum(1 for s in scores if s.application_parity_pct >= 100.0) / total * 100.0
        perf_cov = sum(1 for s in scores if s.performance_contract_parity_pct >= 100.0) / total * 100.0
        adv_cov = sum(1 for s in scores if s.adversarial_parity_pct >= 100.0) / total * 100.0

        # Category break-down
        families = set(s.family.value for s in scores)
        cat_map: Dict[str, float] = {}
        for f in families:
            f_scores = [s for s in scores if s.family.value == f]
            passed = sum(1 for s in f_scores if s.is_100_percent_verified)
            cat_map[f] = round((passed / len(f_scores)) * 100.0, 1)

        return GlobalCoverageMatrix(
            total_required_capabilities=total,
            verified_capabilities_count=verified,
            global_verified_parity_pct=round((verified / total) * 100.0, 1),
            exact_coverage_pct=round(exact_cov, 1),
            contract_coverage_pct=round(ctr_cov, 1),
            application_coverage_pct=round(app_cov, 1),
            performance_contract_coverage_pct=round(perf_cov, 1),
            adversarial_coverage_pct=round(adv_cov, 1),
            blind_holdout_coverage_pct=round(holdout_score * 100.0, 1),
            category_coverage=cat_map,
            capability_scores=scores,
        )
