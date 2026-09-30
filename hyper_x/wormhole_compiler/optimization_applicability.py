import numpy as np
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

@dataclass
class ApplicabilityReport:
    optimization: str
    applicable: bool
    classification: str
    confidence: float
    reason: str
    recommended_action: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    contract_id: Optional[str] = None
    net_gain: Optional[float] = None
    roi: Optional[float] = None
    n_break_even: Optional[float] = None

class OptimizationApplicabilityEngine:
    def __init__(self):
        # Maps (workload, optimization) to status
        self.applicability_matrix: Dict[Tuple[str, str], str] = {}
        self.failure_knowledge_base: List[Dict[str, Any]] = []
        
    def evaluate(self, workload: Any, workload_name: str, contract: Any, optimization: str) -> ApplicabilityReport:
        # Check failure knowledge base
        for failure in self.failure_knowledge_base:
            if failure["workload"] == workload_name and failure["optimization"] == optimization:
                if failure.get("contract_strictness", "") == getattr(contract, "strictness", ""):
                    return ApplicabilityReport(
                        optimization=optimization,
                        applicable=False,
                        classification=failure.get("reason", "UNKNOWN"),
                        confidence=0.99,
                        reason=f"Previously rejected: {failure.get('reason')}",
                        recommended_action="SKIP_AND_SEARCH_ALTERNATIVES",
                        evidence=failure.get("evidence", {})
                    )
        
        if optimization == "LOW_RANK":
            return self._evaluate_low_rank(workload, contract)
        elif optimization == "THRESHOLD_SPARSITY":
            return self._evaluate_threshold_sparsity(workload, contract)
        
        return ApplicabilityReport(
            optimization=optimization,
            applicable=False,
            classification="UNKNOWN",
            confidence=0.0,
            reason=f"No applicability test defined for {optimization}",
            recommended_action="REFERENCE_FALLBACK"
        )
        
    def _evaluate_low_rank(self, workload: Any, contract: Any) -> ApplicabilityReport:
        if not isinstance(workload, np.ndarray) or workload.ndim != 2:
            return ApplicabilityReport(
                optimization="LOW_RANK", applicable=False, classification="INVALID_SHAPE",
                confidence=1.0, reason="Workload is not a 2D matrix", recommended_action="REJECT"
            )
            
        exactness = getattr(contract, 'tolerance', 0.0) == 0.0
        
        # Spectral decay analysis
        U, S, Vt = np.linalg.svd(workload, full_matrices=False)
        r = len(S)
        energy_total = np.sum(S**2)
        
        if energy_total == 0:
            return ApplicabilityReport(
                optimization="LOW_RANK", applicable=False, classification="ZERO_MATRIX",
                confidence=1.0, reason="Matrix is entirely zero", recommended_action="REJECT"
            )
            
        # Rank sweep
        ranks_to_test = [1, 2, 4, 8, 16, 32, 64]
        best_rank = None
        best_error = float('inf')
        
        tested_ranks = []
        for k in ranks_to_test:
            if k >= r:
                break
            energy_k = np.sum(S[:k]**2) / energy_total
            reconstruction_error = 1.0 - energy_k
            tested_ranks.append({"rank": k, "error": reconstruction_error})
            
            if exactness:
                if reconstruction_error == 0.0:
                    best_rank = k
                    best_error = 0.0
                    break
            else:
                if reconstruction_error <= getattr(contract, 'tolerance', 1e-3):
                    best_rank = k
                    best_error = reconstruction_error
                    break
                    
        # Check if flat spectrum
        if r > 1 and S[r-1] / S[0] > 0.1:
            classification = "FLAT_SPECTRUM"
            reason = "No useful rank/error tradeoff under current contract"
            applicable = False
        elif best_rank is not None:
            classification = "STRONG_SPECTRAL_DECAY"
            reason = f"Rank {best_rank} approximation meets contract"
            applicable = True
        else:
            classification = "WEAK_SPECTRAL_DECAY"
            reason = "Cannot reach contract tolerance at useful compression"
            applicable = False
            
        if exactness and applicable:
            if best_rank is None or best_rank >= r:
                applicable = False
                classification = "FULL_RANK_UNSTRUCTURED"
                reason = "Exact contract cannot be met with low rank compression"
            
        return ApplicabilityReport(
            optimization="LOW_RANK",
            applicable=applicable,
            classification=classification,
            confidence=0.95,
            reason=reason,
            recommended_action="DEPLOY" if applicable else "SKIP_AND_SEARCH_ALTERNATIVES",
            evidence={"tested_ranks": tested_ranks, "best_rank": best_rank}
        )

    def _evaluate_threshold_sparsity(self, workload: Any, contract: Any) -> ApplicabilityReport:
        if not isinstance(workload, np.ndarray):
            return ApplicabilityReport(
                optimization="THRESHOLD_SPARSITY", applicable=False, classification="INVALID_TYPE",
                confidence=1.0, reason="Workload not an array", recommended_action="REJECT"
            )
            
        threshold = 1e-2
        original_nnz = workload.size
        remaining_nnz = np.sum(np.abs(workload) > threshold)
        removed_nnz = original_nnz - remaining_nnz
        percentage_removed = (removed_nnz / original_nnz) * 100 if original_nnz > 0 else 0
        
        # Economic applicability
        # If less than 10% removed, overhead of mask generation is likely higher
        if percentage_removed < 10.0:
            return ApplicabilityReport(
                optimization="THRESHOLD_SPARSITY",
                applicable=False,
                classification="LOW_SPARSITY",
                confidence=0.9,
                reason=f"Only {percentage_removed:.1f}% work eliminated while preprocessing adds overhead",
                recommended_action="REJECT",
                evidence={"percentage_removed": percentage_removed}
            )
            
        return ApplicabilityReport(
            optimization="THRESHOLD_SPARSITY",
            applicable=True,
            classification="HIGH_SPARSITY",
            confidence=0.9,
            reason=f"{percentage_removed:.1f}% work eliminated, economically viable",
            recommended_action="DEPLOY",
            evidence={"percentage_removed": percentage_removed}
        )
        
    def record_failure(self, workload_name: str, optimization: str, reason: str, evidence: Dict[str, Any]):
        self.failure_knowledge_base.append({
            "workload": workload_name,
            "optimization": optimization,
            "status": "REJECTED",
            "reason": reason,
            "evidence": evidence
        })
