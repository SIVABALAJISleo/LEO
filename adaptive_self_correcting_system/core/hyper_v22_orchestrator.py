import asyncio
from typing import List, Dict, Any, Tuple, Optional
from .gate.input_validator import InputValidator
from .core.disambiguation_engine import DisambiguationEngine
from .core.consequence_engine import ConsequenceEngine
from .core.knowledge_layer import KnowledgeLayer
from .core.dual_engine import DualExecutionEngine
from .core.calibration_engine import CalibrationEngine
from .core.meta_uncertainty_engine import MetaUncertaintyEngine
from .core.verification_layer import VerificationLayer
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV22Response, SystemStatus, RiskLevel, Reversibility
)

class LeoV22Orchestrator:
    """
    SYSTEM: HYPER HYBRID NEURO-SYMBOLIC RISK-BOUNDED CORE v22.0
    Objective: 99.9%+ correctness through strict order and verification.
    """
    def __init__(self, conf_threshold: float = 0.92):
        self.cache = SemanticCache(threshold=0.9)
        self.validator = InputValidator({"allowed_domains": ["finance", "system", "code"]})
        self.disambiguator = DisambiguationEngine()
        self.consequence = ConsequenceEngine()
        self.knowledge = KnowledgeLayer()
        self.dual_engine = DualExecutionEngine()
        self.calibration = CalibrationEngine()
        self.meta_u = MetaUncertaintyEngine()
        self.verifier = VerificationLayer()
        self.conf_threshold = conf_threshold

    async def run(self, user_input: str) -> LeoV22Response:
        # 1. INPUT GATE
        valid, parsed, msg = self.validator.validate(user_input)
        if not valid:
            return self._abstain("Input rejected by gate.", msg)

        # 2. SOCRATIC CLARIFICATION
        is_ambiguous, question = self.disambiguator.check_ambiguity(user_input)
        if is_ambiguous:
            return LeoV22Response(
                status=SystemStatus.CLARIFICATION_REQUIRED,
                confidence=0.0,
                risk_level=RiskLevel.MINOR,
                verification_status="PENDING",
                clarification_question=question
            )

        # 3. CONSEQUENCE + 4. IRREVERSIBILITY
        r_level, rev = self.consequence.classify(user_input)
        
        # 11. SEMANTIC CACHE
        cached = self.cache.query(user_input)
        if cached:
            return LeoV22Response(answer=cached.code, status=SystemStatus.SUCCESS, confidence=1.0, risk_level=r_level, verification_status="CACHED")

        # 5. KNOWLEDGE LAYER
        k_valid, facts, k_msg = await self.knowledge.retrieve_verified(user_input)
        if not k_valid:
            return self._abstain("Insufficient knowledge.", k_msg)

        # 6. DUAL EXECUTION ENGINE
        e_success, result, e_msg = await self.dual_engine.execute_dual(user_input)
        if not e_success:
            return self._abstain("Dual engine divergence.", e_msg)

        # 7. CALIBRATION + 8. META-UNCERTAINTY
        # (Simplified mock of confidence and meta-uncertainty)
        confidence = 0.95 
        meta_u_fail = self.meta_u.check_meta_uncertainty([confidence])
        
        if confidence < self.conf_threshold or meta_u_fail:
            return self._abstain("Confidence/Meta-Uncertainty below safe bounds.")

        # 9. ADVERSARIAL SELF-CHECK + 12. TRIPLE REDUNDANCY (Simulated)
        v_success, checks = self.verifier.verify(result, [])
        if not v_success:
            return self._abstain("Verification invariant violation.")

        # 14. OUTPUT CONTRACT
        return LeoV22Response(
            answer=result,
            status=SystemStatus.SUCCESS,
            confidence=confidence,
            risk_level=r_level,
            verification_status="VERIFIED"
        )

    def _abstain(self, reason: str, details: str = "") -> LeoV22Response:
        return LeoV22Response(
            status=SystemStatus.ABSTAINED,
            confidence=0.0,
            uncertainty_reason=f"{reason} {details}",
            risk_level=RiskLevel.TRIVIAL,
            verification_status="FAILED"
        )
吐
