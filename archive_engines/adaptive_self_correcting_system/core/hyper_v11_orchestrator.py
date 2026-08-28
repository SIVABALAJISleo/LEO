import asyncio
from typing import List, Any, Optional
from .spec_constructor import SpecConstructor
from .formal_verifier import FormalVerifier
from .reasoning_engine import ReasoningEngine
from .retrieval_validator import RetrievalValidator
from .fusion_engine import AdvancedFusionEngine
from .dependency_tracker import DependencyTracker
from .drift_controller import DriftController
from .memory_manager import LeoAdaptiveMemory
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV11Response, SystemStatus, ReasoningPath
)

class LeoV11Orchestrator:
    """
    SYSTEM: HYPER ERROR-BOUNDED HYBRID CORE v11.0
    Objective: Near-zero error on answered outputs via controlled abstention.
    """
    def __init__(self):
        self.l1_cache = {} # Exact cache
        self.l2_cache = SemanticCache(threshold=0.9)
        self.spec_constructor = SpecConstructor()
        self.formal_verifier = FormalVerifier()
        self.reasoning_engine = ReasoningEngine()
        self.retrieval_validator = RetrievalValidator()
        self.fusion_engine = AdvancedFusionEngine()
        self.dependency_tracker = DependencyTracker()
        self.drift_controller = DriftController()
        self.memory = LeoAdaptiveMemory()
        self.max_iters = 3

    async def run(self, user_input: str) -> LeoV11Response:
        # 11) MEMORY SYSTEM: L1 check
        if user_input in self.l1_cache:
            return self._success_response(self.l1_cache[user_input], 1.0, False, None, ["L1 Exact Hit"])

        # 1) DOMAIN ROUTING & 2) SPEC EXTRACTION
        spec, clarifications = await self.spec_constructor.construct(user_input)
        if not spec:
            return self._uncertain_response(clarifications, "Incomplete spec or out-of-domain")

        # 10) ANYTIME REASONING
        best_solution = None
        for iteration in range(self.max_iters):
            # 3) MULTI-EVIDENCE GENERATION
            paths = await self.reasoning_engine.execute_paths(spec, "HIGH")
            
            # 4) DEPENDENCY CONTROL & 5) EVIDENCE HANDLING
            relationship = self.dependency_tracker.classify_cluster([p.path_id for p in paths])
            agreement_level, conflict_detected = self.fusion_engine.fuse(paths, relationship)
            
            # 6) RETRIEVAL VALIDATION (with TTL/recency logic placeholder)
            r_success, r_agreement, r_conflicts = await self.retrieval_validator.validate(user_input, paths[0].output)
            
            # 7) CONFIDENCE CALIBRATION
            v_results = await asyncio.gather(*[self.formal_verifier.verify(p.output, spec) for p in paths])
            v_pass_rate = sum(1 for r in v_results if r[0]) / len(paths)
            
            # confidence = agreement + verification + retrieval - conflict_penalty - OOD_penalty
            conflict_penalty = 0.2 if conflict_detected else 0.0
            confidence = (agreement_level * 0.4) + (v_pass_rate * 0.4) + (r_agreement * 0.2) - conflict_penalty
            
            # 12) DRIFT CONTROL
            drift_metrics = self.drift_controller.update(confidence)
            if drift_metrics.anomaly_detected:
                confidence -= 0.1 # Penalty for anomaly
            
            # 9) ABSTENTION GATE
            if confidence < 0.85 or conflict_detected:
                # 8) CONFORMAL DECISION
                return self._abstain_response(paths, confidence, conflict_detected)
            
            if confidence >= 0.90:
                best_solution = paths[0]
                break

        if best_solution:
            # Store in L1 cache
            self.l1_cache[user_input] = best_solution.output
            return self._success_response(best_solution.output, confidence, conflict_detected, None, ["Error-bounded consensus reached"])
        
        return self._uncertain_response(["No solution met the strict v11.0 abstention gate."], "Low confidence")

    def _success_response(self, answer: Any, confidence: float, conflict: bool, p_set: Optional[List[Any]], summary: List[str]) -> LeoV11Response:
        return LeoV11Response(
            status=SystemStatus.SUCCESS,
            confidence=confidence * 100,
            verified=True,
            conflict_detected=conflict,
            prediction_set=p_set,
            summary=summary,
            risks=[],
            final_answer=answer
        )

    def _abstain_response(self, paths: List[ReasoningPath], confidence: float, conflict: bool) -> LeoV11Response:
        p_set = list(set([p.output for p in paths]))
        return LeoV11Response(
            status=SystemStatus.UNCERTAIN,
            confidence=confidence * 100,
            verified=False,
            conflict_detected=conflict,
            prediction_set=p_set,
            uncertainty_reason="Significant conflict or low confidence detected. Abstaining for safety.",
            escalation_needed=True,
            summary=["System opted to abstain due to error bounds."],
            risks=["High uncertainty in reasoning paths"]
        )

    def _uncertain_response(self, clarifications: List[str], reason: str) -> LeoV11Response:
        return LeoV11Response(
            status=SystemStatus.UNCERTAIN,
            confidence=0.0,
            verified=False,
            conflict_detected=False,
            uncertainty_reason=reason,
            summary=[],
            risks=clarifications,
            clarification_needed=clarifications
        )

