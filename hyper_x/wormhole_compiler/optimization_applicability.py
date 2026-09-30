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
        elif optimization in ["THRESHOLD_SPARSITY", "SPARSITY"]:
            return self._evaluate_threshold_sparsity(workload, contract)
        elif optimization in ["EXACT_REUSE", "MEMOIZATION"]:
            return self._evaluate_exact_reuse(workload, contract)
        elif optimization in ["DELTA_COMPUTATION", "INCREMENTAL"]:
            return self._evaluate_delta_computation(workload, contract)
        elif optimization in ["PRECISION_REDUCTION", "QUANTIZATION"]:
            return self._evaluate_precision_reduction(workload, contract)
        elif optimization in ["OUTPUT_SENSITIVE_PRUNING", "OUTPUT_PROJECT"]:
            return self._evaluate_output_sensitive_pruning(workload, contract)
        elif optimization in ["MEMORY_TILING", "CACHE_BLOCKING"]:
            return self._evaluate_memory_tiling(workload, contract)
        
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

    def _evaluate_exact_reuse(self, workload: Any, contract: Any) -> ApplicabilityReport:
        cache_policy = getattr(contract, "cache_policy", None)
        if cache_policy is not None:
            policy_val = getattr(cache_policy, "value", str(cache_policy))
            if policy_val in ["COLD", "CachePolicy.COLD"]:
                return ApplicabilityReport(
                    optimization="EXACT_REUSE",
                    applicable=False,
                    classification="CONTRACT_FORBIDS_REUSE",
                    confidence=1.0,
                    reason="Contract explicitly enforces COLD cache policy; memoization reuse is forbidden",
                    recommended_action="REJECT",
                    evidence={"cache_policy": policy_val}
                )
        
        if getattr(contract, "deterministic", True) is False:
            return ApplicabilityReport(
                optimization="EXACT_REUSE",
                applicable=False,
                classification="NON_DETERMINISTIC_WORKLOAD",
                confidence=1.0,
                reason="Workload is non-deterministic; exact memoization cannot be safely reused",
                recommended_action="REJECT"
            )

        if isinstance(workload, (list, tuple)) and len(workload) > 1:
            hashes = set()
            for item in workload:
                if isinstance(item, np.ndarray):
                    hashes.add(item.tobytes()[:256])
                else:
                    hashes.add(id(item))
            unique_ratio = len(hashes) / len(workload)
            if unique_ratio > 0.95:
                return ApplicabilityReport(
                    optimization="EXACT_REUSE",
                    applicable=False,
                    classification="ZERO_HIT_RATE_STREAMING",
                    confidence=0.95,
                    reason=f"Streaming inputs are 100% unique ({unique_ratio*100:.1f}% unique); cryptographic hashing overhead exceeds recomputation with ~0% hit rate",
                    recommended_action="SKIP_AND_SEARCH_ALTERNATIVES",
                    evidence={"unique_ratio": unique_ratio}
                )
        
        return ApplicabilityReport(
            optimization="EXACT_REUSE",
            applicable=True,
            classification="HIGH_REPETITION_POTENTIAL",
            confidence=0.9,
            reason="Workload contract permits memoization and repetition potential exists",
            recommended_action="DEPLOY"
        )

    def _evaluate_delta_computation(self, workload: Any, contract: Any) -> ApplicabilityReport:
        if isinstance(workload, (list, tuple)) and len(workload) >= 2:
            prev, curr = workload[0], workload[1]
            if isinstance(prev, np.ndarray) and isinstance(curr, np.ndarray) and prev.shape == curr.shape:
                delta = curr - prev
                tol = getattr(contract, "tolerance", 0.0)
                active_elements = np.sum(np.abs(delta) > tol)
                active_ratio = float(active_elements) / float(delta.size) if delta.size > 0 else 0.0
                
                if active_ratio > 0.70:
                    return ApplicabilityReport(
                        optimization="DELTA_COMPUTATION",
                        applicable=False,
                        classification="INSUFFICIENT_TEMPORAL_COHERENCE",
                        confidence=0.95,
                        reason=f"High delta entropy ({active_ratio*100:.1f}% active entries changed); delta tracking adds subtraction and indexing overhead without eliminating compute",
                        recommended_action="REJECT",
                        evidence={"active_ratio": active_ratio}
                    )
                
                is_exact = getattr(contract, "tolerance", 0.0) == 0.0 or getattr(contract, "correctness_mode", "") in ["EXACT", "CorrectnessMode.EXACT"]
                if is_exact and active_ratio > 0.30:
                    return ApplicabilityReport(
                        optimization="DELTA_COMPUTATION",
                        applicable=False,
                        classification="DRIFT_SENSITIVE_EXACT",
                        confidence=0.90,
                        reason="Under EXACT contract, accumulating delta state risks floating point drift requiring frequent recomputation checkpoints",
                        recommended_action="REJECT",
                        evidence={"active_ratio": active_ratio}
                    )

                return ApplicabilityReport(
                    optimization="DELTA_COMPUTATION",
                    applicable=True,
                    classification="SPARSE_TEMPORAL_DELTA",
                    confidence=0.95,
                    reason=f"High temporal coherence ({active_ratio*100:.1f}% active changes); incremental delta computation is economically viable",
                    recommended_action="DEPLOY",
                    evidence={"active_ratio": active_ratio}
                )
        
        return ApplicabilityReport(
            optimization="DELTA_COMPUTATION",
            applicable=False,
            classification="STATIC_WORKLOAD_NO_TEMPORAL_DIMENSION",
            confidence=0.90,
            reason="Workload has no sequential temporal dimension; delta recomputation does not apply",
            recommended_action="SKIP_AND_SEARCH_ALTERNATIVES"
        )

    def _evaluate_precision_reduction(self, workload: Any, contract: Any) -> ApplicabilityReport:
        is_exact = getattr(contract, "tolerance", 0.0) == 0.0 or getattr(contract, "correctness_mode", "") in ["EXACT", "CorrectnessMode.EXACT"]
        if is_exact:
            return ApplicabilityReport(
                optimization="PRECISION_REDUCTION",
                applicable=False,
                classification="CONTRACT_DEMANDS_EXACT_PRECISION",
                confidence=1.0,
                reason="Contract specifies EXACT mathematical output (zero tolerance); reducing precision is strictly prohibited by exactness firewall",
                recommended_action="REJECT"
            )

        if isinstance(workload, np.ndarray) and workload.ndim == 2 and workload.size > 0:
            try:
                cond = float(np.linalg.cond(workload))
                if cond > 1e4:
                    return ApplicabilityReport(
                        optimization="PRECISION_REDUCTION",
                        applicable=False,
                        classification="ILL_CONDITIONED_SPECTRUM",
                        confidence=0.95,
                        reason=f"Matrix is severely ill-conditioned (condition number {cond:.2e} > 1e4); precision truncation will cause catastrophic loss of precision",
                        recommended_action="REJECT",
                        evidence={"condition_number": cond}
                    )
            except Exception:
                pass

        return ApplicabilityReport(
            optimization="PRECISION_REDUCTION",
            applicable=True,
            classification="WELL_CONDITIONED_NUMERICAL_SLACK",
            confidence=0.90,
            reason="Workload has sufficient numerical slack and is well-conditioned",
            recommended_action="DEPLOY"
        )

    def _evaluate_output_sensitive_pruning(self, workload: Any, contract: Any) -> ApplicabilityReport:
        observable = getattr(contract, "observable", "output_tensor")
        preserve_shape = getattr(contract, "preserve_shape", True)
        
        if observable in ["output_tensor", "full_tensor", "dense_result"] and preserve_shape:
            if not getattr(contract, "top_k", None) and not getattr(contract, "output_sparsity_mask", None):
                return ApplicabilityReport(
                    optimization="OUTPUT_SENSITIVE_PRUNING",
                    applicable=False,
                    classification="FULL_DENSE_OUTPUT_REQUIRED",
                    confidence=0.95,
                    reason="Contract demands complete dense output tensor; intermediate pruning violates output observable contract",
                    recommended_action="REJECT"
                )

        return ApplicabilityReport(
            optimization="OUTPUT_SENSITIVE_PRUNING",
            applicable=True,
            classification="PRUNABLE_OUTPUT_SUBSPACE",
            confidence=0.90,
            reason="Contract observable allows partial or output-sensitive evaluation",
            recommended_action="DEPLOY"
        )

    def _evaluate_memory_tiling(self, workload: Any, contract: Any) -> ApplicabilityReport:
        if isinstance(workload, np.ndarray):
            nbytes = workload.nbytes
            l1_size = 32 * 1024  # 32KB typical L1 per core
            if nbytes <= l1_size:
                return ApplicabilityReport(
                    optimization="MEMORY_TILING",
                    applicable=False,
                    classification="FITS_IN_L1_CACHE",
                    confidence=0.95,
                    reason=f"Workload footprint ({nbytes} bytes) fits entirely within L1 cache ({l1_size} bytes); loop blocking/tiling adds control overhead without reducing cache misses",
                    recommended_action="REJECT",
                    evidence={"footprint_bytes": nbytes, "l1_size": l1_size}
                )
            
            return ApplicabilityReport(
                optimization="MEMORY_TILING",
                applicable=True,
                classification="CACHE_CAPACITY_EXCEEDED",
                confidence=0.90,
                reason=f"Workload footprint ({nbytes} bytes) exceeds L1 cache; memory tiling will improve spatial and temporal cache locality",
                recommended_action="DEPLOY",
                evidence={"footprint_bytes": nbytes}
            )

        return ApplicabilityReport(
            optimization="MEMORY_TILING",
            applicable=False,
            classification="UNKNOWN_FOOTPRINT",
            confidence=0.5,
            reason="Workload has undefined memory footprint for cache tiling analysis",
            recommended_action="SKIP_AND_SEARCH_ALTERNATIVES"
        )
        
    def record_failure(self, workload_name: str, optimization: str, reason: str, evidence: Dict[str, Any]):
        self.failure_knowledge_base.append({
            "workload": workload_name,
            "optimization": optimization,
            "status": "REJECTED",
            "reason": reason,
            "evidence": evidence
        })
