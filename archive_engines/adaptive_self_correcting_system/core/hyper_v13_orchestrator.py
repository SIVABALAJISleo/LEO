import asyncio
from typing import List, Any
from .spec_constructor import SpecConstructor
from .formal_verifier import FormalVerifier
from .reasoning_engine import ReasoningEngine
from .retrieval_validator import RetrievalValidator
from .fusion_engine import AdvancedFusionEngine
from .dependency_tracker import DependencyTracker
from .drift_controller import DriftController
from .risk_engine import RiskEngine
from .memory_manager import LeoAdaptiveMemory
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV12Response, SystemStatus
)

class LeoV13Orchestrator:
    """
    SYSTEM: HYPER RISK-BOUNDED OUTPUT CORE v13.0
    Objective: Near-zero error on committed outputs via auditable risk bounds.
    """
    def __init__(self, risk_threshold: float = 0.05):
        self.l1_cache = {}
        self.l2_cache = SemanticCache(threshold=0.9)
        self.spec_constructor = SpecConstructor()
        self.formal_verifier = FormalVerifier()
        self.reasoning_engine = ReasoningEngine()
        self.retrieval_validator = RetrievalValidator()
        self.fusion_engine = AdvancedFusionEngine()
        self.dependency_tracker = DependencyTracker()
        self.drift_controller = DriftController()
        self.risk_engine = RiskEngine(risk_threshold=risk_threshold)
        self.memory = LeoAdaptiveMemory()
        self.max_iters = 3

    async def run(self, user_input: str) -> LeoV12Response:
        # 11) MEMORY SYSTEM
        if user_input in self.l1_cache:
            return self._commit_response(self.l1_cache[user_input], 1.0, 0.0, False, ["Verified L1 Commit"])

        # 2) SPEC EXTRACTION
        spec, clarifications = await self.spec_constructor.construct(user_input)
        if not spec:
            return self._abstain_response("Incomplete spec or out-of-domain", clarifications)

        # 10) ANYTIME REASONING
        for iteration in range(self.max_iters):
            # 3) MULTI-EVIDENCE GENERATION
            paths = await self.reasoning_engine.execute_paths(spec, "HIGH")
            
            # 4) DEPENDENCY CONTROL (Statistical Decorrelation)
            relationship = self.dependency_tracker.classify_cluster([p.path_id for p in paths])
            agreement_level, conflict_detected = self.fusion_engine.fuse(paths, relationship)
            
            # 6) RETRIEVAL VALIDATION
            r_success, r_agreement, r_conflicts = await self.retrieval_validator.validate(user_input, paths[0].output)
            
            # 7) CALIBRATION LAYER
            v_results = await asyncio.gather(*[self.formal_verifier.verify(p.output, spec) for p in paths])
            v_pass_rate = sum(1 for r in v_results if r[0]) / len(paths)
            
            # Calibration logic
            confidence = (agreement_level * 0.4) + (v_pass_rate * 0.4) + (r_agreement * 0.2)
            
            # 8) RISK ESTIMATION (delta_est)
            risk_metrics = self.risk_engine.calculate_risk(paths, confidence)
            
            # 9) COMMIT GATE
            if risk_metrics.is_acceptable and not conflict_detected and v_pass_rate > 0.8:
                # COMMIT answer
                best_solution = paths[0]
                self.l1_cache[user_input] = best_solution.output
                return self._commit_response(best_solution.output, confidence, risk_metrics.risk_level, False, ["Risk-bounded commit (delta_est <= threshold)"])
            
            if iteration == self.max_iters - 1:
                # ABSTAIN
                return self._abstain_response(
                    f"Error probability (delta_est: {risk_metrics.risk_level:.3f}) exceeds threshold.",
                    ["Risk too high for commitment" if risk_metrics.risk_level > self.risk_engine.risk_threshold else "Conflict detected"]
                )

        return self._abstain_response("Max iterations reached without reaching risk bound.", [])

    def _commit_response(self, answer: Any, confidence: float, risk: float, conflict: bool, summary: List[str]) -> LeoV12Response:
        return LeoV12Response(
            status=SystemStatus.SUCCESS,
            confidence=confidence * 100,
            risk_bound=risk,
            verified=True,
            conflict_detected=conflict,
            summary=summary
        )

    def _abstain_response(self, reason: str, risks: List[str]) -> LeoV12Response:
        return LeoV12Response(
            status=SystemStatus.UNCERTAIN,
            confidence=0.0,
            verified=False,
            conflict_detected=True,
            summary=["System ABSTAINED to maintain risk bounds."],
            reason=reason,
            risks=risks,
            escalation_needed=True
        )

