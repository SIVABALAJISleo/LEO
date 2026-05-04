import asyncio
import time
from typing import List, Dict, Any, Tuple, Optional
from .spec_constructor import SpecConstructor
from .formal_verifier import FormalVerifier
from .reasoning_engine import ReasoningEngine
from .retrieval_validator import RetrievalValidator
from .fusion_engine import FusionEngine
from .memory_manager import LeoAdaptiveMemory
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV8Response, LeoV4Spec, SystemStatus, ReasoningPath
)

class LeoV8Orchestrator:
    """
    SYSTEM: HYPER UNCERTAINTY-AWARE VERIFIED CORE v8.0
    Objective: Maximize correctness via multi-evidence reasoning and conflict awareness.
    """
    def __init__(self):
        self.cache = SemanticCache(threshold=0.9)
        self.spec_constructor = SpecConstructor()
        self.formal_verifier = FormalVerifier()
        self.reasoning_engine = ReasoningEngine()
        self.retrieval_validator = RetrievalValidator()
        self.fusion_engine = FusionEngine()
        self.memory = LeoAdaptiveMemory()
        self.max_iters = 3

    async def run(self, user_input: str) -> LeoV8Response:
        # 8) CACHE CONTROL
        cached = self.cache.query(user_input)
        if cached:
            return self._success_response(cached.code, 1.0, 1.0, False, ["Verified Cache Hit"])

        # 1) DOMAIN ROUTING & 2) SPEC EXTRACTION
        spec, clarifications = await self.spec_constructor.construct(user_input)
        if not spec:
            return self._uncertain_response(clarifications)

        # 8) ANYTIME LOOP
        best_solution = None
        for iteration in range(self.max_iters):
            # 3) MULTI-AGENT GENERATION (top 3–5 paths)
            paths = await self.reasoning_engine.execute_paths(spec, "HIGH")
            paths = paths[:5]
            
            # 4) EVIDENCE FUSION
            agreement_level, conflict_detected = self.fusion_engine.fuse_evidence(paths)
            
            # 5) CONSENSUS + ADVERSARY
            # (Adversary check integrated in verification)
            v_results = await asyncio.gather(*[self.formal_verifier.verify(p.output, spec) for p in paths])
            v_pass_count = sum(1 for r in v_results if r[0])
            verification_pass_rate = v_pass_count / len(paths) if paths else 0
            
            # 6) RETRIEVAL VALIDATION
            r_success, r_agreement, r_conflicts = await self.retrieval_validator.validate(user_input, paths[0].output if paths else None)
            
            # 7) CONFIDENCE CALCULATION
            # confidence = (agreement * 0.35) + (verification * 0.35) + (retrieval * 0.2) + (conflict_penalty * 0.1)
            conflict_penalty = 1.0 if not conflict_detected else 0.0
            confidence = (agreement_level * 0.35) + (verification_pass_rate * 0.35) + (r_agreement * 0.2) + (conflict_penalty * 0.1)
            
            # 11) OUTPUT GATE
            if confidence >= 0.90 and not conflict_detected:
                best_solution = paths[0]
                break
            
            # If significant conflict, prefer uncertainty
            if agreement_level < 0.6:
                break

        if best_solution and confidence >= 0.90:
            return self._success_response(best_solution.output, confidence, agreement_level, conflict_detected, ["Multi-evidence consensus reached"])
        else:
            return LeoV8Response(
                status=SystemStatus.UNCERTAIN,
                confidence=confidence * 100,
                verified=False,
                agreement_level=agreement_level,
                conflict_detected=conflict_detected,
                reasoning_summary=["Conflict detected or low consensus"],
                risks=["Divergent reasoning paths" if conflict_detected else "Low verification pass rate"],
                clarification_needed=["Please provide more context to resolve internal disagreements."]
            )

    def _success_response(self, answer: Any, confidence: float, agreement: float, conflict: bool, summary: List[str]) -> LeoV8Response:
        return LeoV8Response(
            status=SystemStatus.SUCCESS,
            confidence=confidence * 100,
            verified=True,
            agreement_level=agreement,
            conflict_detected=conflict,
            reasoning_summary=summary,
            risks=[],
            clarification_needed=[],
            final_answer=answer
        )

    def _uncertain_response(self, clarifications: List[str]) -> LeoV8Response:
        return LeoV8Response(
            status=SystemStatus.UNCERTAIN,
            confidence=0.0,
            verified=False,
            agreement_level=0.0,
            conflict_detected=False,
            reasoning_summary=[],
            risks=clarifications,
            clarification_needed=clarifications
        )
吐
