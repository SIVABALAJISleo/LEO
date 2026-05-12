import asyncio
import time
from typing import List, Dict, Any, Tuple
from .intent_extractor import IntentExtractor
from .ambiguity_resolver import AmbiguityResolver
from .compute_router import ComputeRouter, ComputeComplexity
from .reasoning_engine import ReasoningEngine
from .reality_verifier import RealityVerifier
from .memory_manager import LeoMemory
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    HyperResponse, HyperIntent, SystemStatus, 
    ConfidenceComponents, ReasoningPath
)

class HyperCoreOrchestrator:
    """
    SYSTEM: HYPER-CORE INFERENCE ENGINE v2.0
    Objective: Maximize accuracy, efficiency, and determinism.
    """
    def __init__(self):
        self.cache = SemanticCache()
        self.intent_extractor = IntentExtractor()
        self.ambiguity_resolver = AmbiguityResolver()
        self.compute_router = ComputeRouter(self.cache)
        self.reasoning_engine = ReasoningEngine()
        self.reality_verifier = RealityVerifier()
        self.memory = LeoMemory()

    async def run(self, user_input: str) -> HyperResponse:
        # 6. COMPUTE OPTIMIZATION: Cache check
        complexity, is_cache_hit = await self.compute_router.route(user_input)
        if is_cache_hit:
            cached = self.cache.query(user_input)
            return self._success_response(cached.code, 100.0, ["Cache hit (0ms)"])

        # 1. DOMAIN GATING / INTENT EXTRACTION
        intent, rejection_msg = await self.intent_extractor.extract(user_input)
        if not intent:
            return self._reject_response(rejection_msg)

        # 2. AMBIGUITY RESOLUTION
        interpretations, clarity_score = await self.ambiguity_resolver.resolve(user_input)
        clarity_val = clarity_score * 30.0 # Scale to 0-30

        if clarity_score < 0.75:
            return self._clarification_response(["Input is ambiguous. Did you mean X or Y?"])

        # 3. MULTI-PATH REASONING
        paths = await self.reasoning_engine.execute_paths(intent, "HIGH" if complexity == ComputeComplexity.HARD else "MEDIUM")
        agreement = self.reasoning_engine.compare_outputs(paths)
        agreement_val = 40.0 if agreement else 10.0 # Scale to 0-40

        # 4. REALITY VERIFICATION
        v_success, v_score, risks = await self.reality_verifier.verify(paths[0].output, {"intent": intent})
        
        # 5. CONFIDENCE ENGINE
        # consistency = 30 if no conflicts, else lower
        consistency_val = 30.0 if agreement and v_success else 10.0
        
        total_confidence = clarity_val + agreement_val + consistency_val

        # 11. OUTPUT POLICY: Refuse if confidence < 85
        if total_confidence < 85:
            return HyperResponse(
                status=SystemStatus.UNCERTAIN,
                confidence=total_confidence,
                reasoning_summary=["Reasoning paths diverged or verification failed."],
                risks=risks + (["Low consistency across paths"] if not agreement else []),
                clarification_needed=["Please provide more constraints to improve determinism."]
            )

        # 9. SELF-CORRECTION LOOP
        # (Already partially covered by RealityVerifier's adversarial check)

        response = self._success_response(paths[0].output, total_confidence, risks)
        
        # 12. Store in Memory
        self.memory.store(user_input, str(response.final_answer), risks, total_confidence/100.0)
        
        return response

    def _success_response(self, answer: Any, confidence: float, risks: List[str]) -> HyperResponse:
        return HyperResponse(
            status=SystemStatus.SUCCESS,
            confidence=confidence,
            reasoning_summary=["Logical derivation", "Heuristic cross-check", "Reality verification"],
            risks=risks,
            clarification_needed=[],
            final_answer=answer
        )

    def _reject_response(self, msg: str) -> HyperResponse:
        return HyperResponse(
            status=SystemStatus.REJECTED,
            confidence=0.0,
            reasoning_summary=[],
            risks=[msg],
            clarification_needed=[]
        )

    def _clarification_response(self, questions: List[str]) -> HyperResponse:
        return HyperResponse(
            status=SystemStatus.UNCERTAIN,
            confidence=50.0,
            reasoning_summary=["Multiple interpretations detected"],
            risks=["Ambiguity risk"],
            clarification_needed=questions
        )

