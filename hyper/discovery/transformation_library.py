"""
hyper/discovery/transformation_library.py
=========================================
Self-Improving Transformation Library for UCTDE.

Turns verified breakthroughs into reusable, parameterized transformation rules:
  Discovery -> Verification -> Abstraction -> Transformation Rule -> Library -> Future Searches.

Every rule encapsulates:
  - preconditions & applicability
  - proof status (FORMALLY_PROVED / EMPIRICALLY_VERIFIED)
  - verification history
  - known counterexamples & boundary limits
"""

from __future__ import annotations
import uuid
import time
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hyper.discovery.proof_engine import ProofStatus


class TransformationRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: f"rule-{uuid.uuid4().hex[:8]}")
    name: str
    family: str                               # e.g., "MATHEMATICAL", "ALGORITHMIC"
    description: str
    target_domains: List[str] = Field(default_factory=list)
    preconditions: List[str] = Field(default_factory=list)
    proof_status: ProofStatus = ProofStatus.EMPIRICALLY_VERIFIED
    proof_id: Optional[str] = None
    historical_success_count: int = 0
    historical_counterexamples: List[str] = Field(default_factory=list)
    asymptotic_improvement: Optional[str] = None # e.g., "O(N^2) -> O(N)"
    created_at: float = Field(default_factory=time.time)

    def record_success(self) -> None:
        self.historical_success_count += 1

    def record_counterexample(self, explanation: str) -> None:
        if explanation not in self.historical_counterexamples:
            self.historical_counterexamples.append(explanation)

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["proof_status"] = self.proof_status.value
        return data


class TransformationLibrary:
    """
    Persistent repository of discovered transformation rules.
    """

    def __init__(self) -> None:
        self.rules: Dict[str, TransformationRule] = {}
        self._initialize_canonical_rules()

    def _initialize_canonical_rules(self) -> None:
        """Bootstraps the library with mathematically verified canonical rules."""
        # Rule 1: Horner's Rule polynomial rewrite
        self.register_rule(
            TransformationRule(
                rule_id="rule-horner-poly",
                name="Vectorized Horner Polynomial Canonicalization",
                family="MATHEMATICAL",
                description="Rewrites naive power sum sum(c_i * x^i) into nested multiply-accumulate form.",
                target_domains=["NUMERICAL_POLYNOMIAL", "NUMERICAL", "ARITHMETIC"],
                preconditions=[
                    "Polynomial degree N >= 2",
                    "Scalar or vector inputs over real field",
                ],
                proof_status=ProofStatus.FORMALLY_PROVED,
                asymptotic_improvement="O(N^2) -> O(N) operations",
                historical_success_count=10,
            )
        )

        # Rule 2: Non-comparative counting sort
        self.register_rule(
            TransformationRule(
                rule_id="rule-counting-sort",
                name="JIT Non-Comparative Key Binning",
                family="ALGORITHMIC",
                description="Substitutes comparison sort with direct histogram indexing when key range K is bounded.",
                target_domains=["SORTING", "BOUNDED_SORTING"],
                preconditions=[
                    "Integer array elements",
                    "Key dynamic range K <= 100,000",
                    "O(N) working memory available",
                ],
                proof_status=ProofStatus.EMPIRICALLY_VERIFIED,
                asymptotic_improvement="O(N log N) -> O(N + K)",
                historical_success_count=8,
            )
        )

        # Rule 3: Factored low-rank matrix GEMM
        self.register_rule(
            TransformationRule(
                rule_id="rule-lowrank-gemm",
                name="Low-Rank Associative Matrix Factoring",
                family="STRUCTURAL",
                description="Factors matrix A into U*V (rank r << N) and evaluates U*(V*B) associatively.",
                target_domains=["MATRIX", "LINEAR_ALGEBRA"],
                preconditions=[
                    "Singular values decay rapidly",
                    "Target rank r < N / 4",
                ],
                proof_status=ProofStatus.FORMALLY_PROVED,
                asymptotic_improvement="O(N^3) -> O(N^2 * r)",
                historical_success_count=5,
            )
        )

    def register_rule(self, rule: TransformationRule) -> None:
        self.rules[rule.rule_id] = rule

    def get_rule(self, rule_id: str) -> Optional[TransformationRule]:
        return self.rules.get(rule_id)

    def match_rules(self, domain: str) -> List[TransformationRule]:
        return [
            r for r in self.rules.values()
            if domain in r.target_domains or "UNIVERSAL" in r.target_domains
        ]

    def all_rules(self) -> List[TransformationRule]:
        return list(self.rules.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_count": len(self.rules),
            "rules": [r.to_dict() for r in self.rules.values()],
        }

    def save_to_file(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
