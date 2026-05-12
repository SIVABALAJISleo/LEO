import asyncio
from typing import List, Dict, Any, Tuple, Optional
from .input_sanitizer import InputSanitizer
from .consequence_engine import ConsequenceEngine
from .reasoning_engine import ReasoningEngine
from .trust_engine import ConsensusEngine, TrustEngine
from .meta_uncertainty_engine import MetaUncertaintyEngine
from .verification_layer import VerificationLayer
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV23Response, SystemStatus, RiskLevel
)

class LeoV23Orchestrator:
    """
    SYSTEM: HYPER HYBRID HIGH-RELIABILITY CORE v23.0
    Objective: 99.5% correctness through consensus and strict abstention.
    """
    def __init__(self, trust_threshold: float = 0.90):
        self.cache = SemanticCache(threshold=0.9)
        self.sanitizer = InputSanitizer()
        self.consequence = ConsequenceEngine()
        self.reasoner = ReasoningEngine()
        self.consensus = ConsensusEngine()
        self.trust_engine = TrustEngine()
        self.meta_u = MetaUncertaintyEngine()
        self.verifier = VerificationLayer()
        self.trust_threshold = trust_threshold

    async def run(self, user_input: str) -> LeoV23Response:
        # 1. INPUT SANITIZATION
        is_valid, clean_input, error_msg = self.sanitizer.sanitize(user_input)
        if not is_valid:
            status = SystemStatus.CLARIFICATION_REQUIRED if "AMBIGUOUS" in error_msg else SystemStatus.ABSTAINED
            return self._abstain(error_msg, status=status)

        # 2. RISK + CONSEQUENCE
        r_level, _ = self.consequence.classify(clean_input)
        
        # 14. SEMANTIC CACHE
        cached = self.cache.query(clean_input)
        if cached:
            return LeoV23Response(answer=cached.code, confidence=1.0, risk_level=r_level, verification_status="CACHED", status=SystemStatus.SUCCESS)

        # 3. MULTI-PATH REASONING
        # Generate 3 paths for consensus
        tasks = [self.reasoner.execute_paths(clean_input, "MEDIUM") for _ in range(3)]
        path_results = await asyncio.gather(*tasks)
        outputs = [p[0].output for p in path_results]

        # 4. CONSENSUS + 6. CONTRADICTION
        has_consensus, winner, agreement = self.consensus.check_consensus(outputs)
        
        # 5. DATA TRUST SCORING
        trust_score = self.trust_engine.calculate_trust(0.95, agreement, 1.0)
        
        # 8. META-UNCERTAINTY
        meta_u_fail = self.meta_u.check_meta_uncertainty([agreement])

        # 9. ABSTENTION ENGINE (CRITICAL)
        if not has_consensus or trust_score < self.trust_threshold or meta_u_fail:
            return self._abstain(f"Consensus failure or low trust score ({trust_score:.2f}).")

        # Final Verification
        v_success, checks = self.verifier.verify(winner, [])
        if not v_success:
            return self._abstain("Final verification invariant check failed.")

        return LeoV23Response(
            answer=winner,
            confidence=trust_score,
            risk_level=r_level,
            verification_status="VERIFIED",
            status=SystemStatus.SUCCESS
        )

    def _abstain(self, reason: str, status: SystemStatus = SystemStatus.ABSTAINED) -> LeoV23Response:
        return LeoV23Response(
            status=status,
            confidence=0.0,
            uncertainty_reason=reason,
            risk_level=RiskLevel.TRIVIAL,
            verification_status="FAILED"
        )

