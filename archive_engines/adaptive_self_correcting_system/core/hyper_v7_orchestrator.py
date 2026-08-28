from typing import List, Dict, Any, Optional
from .spec_constructor import SpecConstructor
from .formal_verifier import FormalVerifier
from .reasoning_engine import ReasoningEngine
from .retrieval_validator import RetrievalValidator
from .memory_manager import LeoAdaptiveMemory
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV4Response, LeoV4Spec, SystemStatus, ReasoningPath
)

class LeoV7Orchestrator:
    """
    SYSTEM: HYPER HYBRID VERIFIED CORE v7.0
    Objective: Return ONLY high-confidence, verified outputs via strict routing.
    """
    def __init__(self):
        self.cache = SemanticCache(threshold=0.9)
        self.spec_constructor = SpecConstructor()
        self.formal_verifier = FormalVerifier()
        self.reasoning_engine = ReasoningEngine()
        self.retrieval_validator = RetrievalValidator()
        self.memory = LeoAdaptiveMemory()
        self.max_iters = 3

    async def run(self, user_input: str) -> LeoV4Response:
        # 0. Cache check
        cached = self.cache.query(user_input)
        if cached:
            return self._success_response(cached.code, 1.0, ["Verified Cache Hit"])

        # 1) DOMAIN ROUTING (HARD GATE)
        # CLOSED = {code, math, structured transforms}
        input_lower = user_input.lower()
        closed_domains = ["python", "code", "math", "calculate", "json", "csv"]
        is_closed = any(d in input_lower for d in closed_domains)

        # 2) SPEC EXTRACTION
        spec, clarifications = await self.spec_constructor.construct(user_input)
        if not spec:
            return self._uncertain_response(clarifications)

        # 8) ANYTIME LOOP
        best_solution = None
        for iteration in range(self.max_iters):
            # 3) MULTI-PATH (LIMITED to top_k=3)
            paths = await self.reasoning_engine.execute_paths(spec, "HIGH")
            paths = paths[:3] 
            
            if is_closed:
                # VERIFIED PIPELINE ONLY
                best_solution = await self._run_verified_pipeline(spec, paths)
            else:
                # HYBRID PIPELINE
                best_solution = await self._run_hybrid_pipeline(user_input, spec, paths)
            
            if best_solution:
                break

        # 9) OUTPUT GATE (STRICT)
        if best_solution:
            confidence = best_solution.get("confidence", 0.0)
            if confidence >= 0.90:
                return self._success_response(best_solution["output"], confidence, ["Verified output via v7.0 pipeline"])
        
        return LeoV4Response(
            status=SystemStatus.UNCERTAIN,
            confidence=0.5,
            verified=False,
            reasoning_summary=["Failed strict confidence gate (0.90)"],
            risks=["Confidence below threshold" if best_solution else "No valid solution found"],
            clarification_needed=["Please provide more constraints to increase certainty."]
        )

    async def _run_verified_pipeline(self, spec: LeoV4Spec, paths: List[ReasoningPath]) -> Optional[Dict[str, Any]]:
        # 4) VERIFICATION CORE (CLOSED ONLY)
        for path in paths:
            v_pass, v_errors = await self.formal_verifier.verify(path.output, spec)
            if v_pass:
                # 6) CONFIDENCE CALIBRATION (Closed)
                # verify_pass is 1.0, retrieval is irrelevant (0)
                # agreement assumed high if multi-path matches
                return {"output": path.output, "confidence": 1.0}
        return None

    async def _run_hybrid_pipeline(self, user_input: str, spec: LeoV4Spec, paths: List[ReasoningPath]) -> Optional[Dict[str, Any]]:
        # 5) RETRIEVAL VALIDATION (HYBRID)
        if not paths: return None
        path = paths[0]
        
        r_success, r_agreement, r_conflicts = await self.retrieval_validator.validate(user_input, path.output)
        v_pass, v_errors = await self.formal_verifier.verify(path.output, spec)
        
        # 6) CONFIDENCE CALIBRATION
        # confidence = 0.4 * path_agreement + 0.4 * verification_pass + 0.2 * retrieval_consistency
        agreement_val = 1.0 # Simplified
        verification_val = 1.0 if v_pass else 0.0
        retrieval_val = r_agreement
        
        confidence = (0.4 * agreement_val) + (0.4 * verification_val) + (0.2 * retrieval_val)
        
        if r_success or v_pass:
            return {"output": path.output, "confidence": confidence}
        return None

    def _success_response(self, answer: Any, confidence: float, summary: List[str]) -> LeoV4Response:
        return LeoV4Response(
            status=SystemStatus.SUCCESS,
            confidence=confidence * 100,
            verified=True,
            reasoning_summary=summary,
            risks=[],
            clarification_needed=[],
            final_answer=answer
        )

    def _uncertain_response(self, clarifications: List[str]) -> LeoV4Response:
        return LeoV4Response(
            status=SystemStatus.UNCERTAIN,
            confidence=0.0,
            verified=False,
            reasoning_summary=[],
            risks=clarifications,
            clarification_needed=clarifications
        )

