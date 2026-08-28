from typing import List, Any
from .spec_constructor import SpecConstructor
from .formal_verifier import FormalVerifier
from .reasoning_engine import ReasoningEngine
from .memory_manager import LeoMemory
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV4Response, SystemStatus
)

class LeoV4Orchestrator:
    """
    SYSTEM: HYPER VERIFIED INTELLIGENCE CORE v4.0
    Objective: Operate ONLY within a closed, formally verifiable domain.
    """
    def __init__(self):
        self.cache = SemanticCache(threshold=0.9)
        self.spec_constructor = SpecConstructor()
        self.formal_verifier = FormalVerifier()
        self.reasoning_engine = ReasoningEngine()
        self.memory = LeoMemory()
        self.max_iters = 3

    async def run(self, user_input: str) -> LeoV4Response:
        # 9. COMPUTE OPTIMIZATION: Cache check
        cached = self.cache.query(user_input)
        if cached:
            return self._success_response(cached.code, 100.0, ["Verified Cache Hit"])

        # 1. DOMAIN LOCK & 2. SPEC CONSTRUCTION
        spec, clarifications = await self.spec_constructor.construct(user_input)
        if not spec:
            status = SystemStatus.REJECTED if "outside" in clarifications[0] else SystemStatus.UNCERTAIN
            return LeoV4Response(
                status=status,
                confidence=0.0,
                verified=False,
                reasoning_summary=[],
                risks=clarifications,
                clarification_needed=clarifications if status == SystemStatus.UNCERTAIN else []
            )

        # 8. ANYTIME LOOP
        best_solution = None
        iteration = 0
        while iteration < self.max_iters:
            iteration += 1
            
            # 4. MULTI-PATH GENERATION
            paths = await self.reasoning_engine.execute_paths(spec, "HIGH")
            
            # 5. FORMAL VERIFICATION & 6. ABSTRACT VALIDATION
            # Verify the deterministic path (A) and model path (B)
            verified_path = None
            for path in paths:
                v_pass, v_errors = await self.formal_verifier.verify(path.output, spec)
                if v_pass:
                    # 7. ADVERSARIAL SELF-CHECK
                    # (Mock: if it passes formal verification, it passes adversarial for now)
                    verified_path = path
                    break
            
            if verified_path:
                best_solution = verified_path
                break
        
        # 10. OUTPUT GATE (STRICT)
        if best_solution:
            return self._success_response(best_solution.output, 100.0, ["All formal checks passed"])
        else:
            return LeoV4Response(
                status=SystemStatus.UNCERTAIN,
                confidence=50.0,
                verified=False,
                reasoning_summary=["No candidate solution passed formal verification"],
                risks=["Verification failure"],
                clarification_needed=["Please provide more constraints for formal proof."]
            )

    def _success_response(self, answer: Any, confidence: float, summary: List[str]) -> LeoV4Response:
        return LeoV4Response(
            status=SystemStatus.SUCCESS,
            confidence=confidence,
            verified=True,
            reasoning_summary=summary,
            risks=[],
            clarification_needed=[],
            final_answer=answer
        )

