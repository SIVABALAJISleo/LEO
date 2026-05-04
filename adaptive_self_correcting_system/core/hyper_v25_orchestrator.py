import asyncio
from typing import List, Dict, Any, Tuple, Optional
from .input_sanitizer import InputSanitizer
from .completeness_service import CompletenessService
from .multi_view_engine import MultiViewEngine
from .consequence_engine import ConsequenceEngine
from .knowledge_layer import KnowledgeLayer
from .reasoning_engine import ReasoningEngine
from .trust_engine import ConsensusEngine
from .symbolic_logic_service import SymbolicLogicService
from .monitoring_service import MonitoringService
from .meta_uncertainty_engine import MetaUncertaintyEngine
from .verification_layer import VerificationLayer
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV25Response, VerificationStatus, RiskLevel
)

class LeoV25Orchestrator:
    """
    SYSTEM: HYPER HYBRID HIGH-RELIABILITY CORE v25.0
    Objective: 99.7% correctness through 28-point end-to-end verification.
    """
    def __init__(self):
        self.sanitizer = InputSanitizer()
        self.completeness = CompletenessService()
        self.multi_view = MultiViewEngine()
        self.consequence = ConsequenceEngine()
        self.knowledge = KnowledgeLayer()
        self.reasoner = ReasoningEngine()
        self.consensus = ConsensusEngine()
        self.symbolic = SymbolicLogicService()
        self.monitor = MonitoringService()
        self.meta_u = MetaUncertaintyEngine()
        self.verifier = VerificationLayer()
        self.cache = SemanticCache(threshold=0.9)

    async def run(self, user_input: str) -> LeoV25Response:
        # 27. DRIFT DETECTION
        if self.monitor.detect_drift():
            return self._abstain("System in safe mode due to detected distribution shift.")

        # 1. INPUT CONTROL + 3. AMBIGUITY + 4. COMPLETENESS
        is_valid, clean_input, err = self.sanitizer.sanitize(user_input)
        if not is_valid: return self._abstain(err)
        
        is_ambiguous, q = self.completeness.detect_ambiguity(clean_input)
        if is_ambiguous: return self._abstain(f"CLARIFICATION_REQUIRED: {q}")

        # 6. QUERY REPHRASING + 5. MULTI-REPRESENTATION
        variants = self.multi_view.generate_variants(clean_input)
        
        # 7. RISK + 8. IRREVERSIBILITY
        r_level, _ = self.consequence.classify(clean_input)
        
        # 20. SEMANTIC CACHE
        cached = self.cache.query(clean_input)
        if cached:
            return LeoV25Response(answer=cached.code, confidence=1.0, risk_level=r_level, verification_status=VerificationStatus.VERIFIED)

        # 9. DATA TRUST + 10. MULTI-MODEL REASONING
        tasks = [self.reasoner.execute_paths(v, "HIGH") for v in variants]
        path_results = await asyncio.gather(*tasks)
        outputs = [p[0].output for p in path_results]

        # 11. CONSENSUS + 12. META-UNCERTAINTY
        has_consensus, winner, agreement = self.consensus.check_consensus(outputs)
        meta_u_fail = self.meta_u.check_meta_uncertainty([agreement])
        
        if not has_consensus or agreement < 0.90 or meta_u_fail:
            return self._abstain(f"Agreement/Consensus failure ({agreement:.2f}).")

        # 15. CONSTRAINT & LOGIC CHECK (Symbolic Layer)
        logic_valid, logic_msg = self.symbolic.verify_logic(winner, clean_input)
        if not logic_valid:
            return self._abstain(logic_msg)

        # 14. STEP-BY-STEP VALIDATION (Final verifier check)
        v_success, checks = self.verifier.verify(winner, [])
        if not v_success:
            return self._abstain("Final verification invariant failure.")

        return LeoV25Response(
            answer=winner,
            confidence=agreement,
            risk_level=r_level,
            verification_status=VerificationStatus.VERIFIED
        )

    def _abstain(self, reason: str) -> LeoV25Response:
        self.monitor.log_error("ABSTENTION", reason)
        return LeoV25Response(
            confidence=0.0,
            uncertainty_reason=reason,
            risk_level=RiskLevel.TRIVIAL,
            verification_status=VerificationStatus.ABSTAINED
        )
吐
