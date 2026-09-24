"""
Escape Engine Types: Standard taxonomy for the 7 classes of computational escape.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from hyper_universal.types import CacheRegime, ResultTaxonomy

class EscapeClass(str, Enum):
    A_ELIMINATION = "ELIMINATION"
    B_SUBSTITUTION = "SUBSTITUTION"
    C_REUSE = "REUSE"
    D_COMPRESSION = "COMPRESSION"
    E_PREDICTION_CORRECTION = "PREDICTION_CORRECTION"
    F_REPRESENTATION_ESCAPE = "REPRESENTATION_ESCAPE"
    G_ALGORITHMIC_ESCAPE = "ALGORITHMIC_ESCAPE"

@dataclass
class EscapeHypothesis:
    """A formal counterfactual escape hypothesis."""
    hypothesis_id: str
    escape_class: EscapeClass
    description: str
    target_operation: str
    proposed_transformation: str
    verification_condition: str
    assumptions: List[str] = field(default_factory=list)
    requires_exact_contract: bool = True
    cache_regime: CacheRegime = CacheRegime.COLD
    expected_work_reduction_ratio: float = 0.0

@dataclass
class EscapeResult:
    """The result of attempting to execute and verify an escape hypothesis."""
    hypothesis_id: str
    escape_class: EscapeClass
    executed: bool
    status: ResultTaxonomy
    measured_speedup: float
    work_eliminated_ratio: float
    verification_passed: bool
    details: Dict[str, Any] = field(default_factory=dict)
    candidate_code: Optional[str] = None
