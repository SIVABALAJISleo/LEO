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
from .belief_engine import BeliefEngine
from .calibration_engine import CalibrationEngine
from .meta_uncertainty_engine import MetaUncertaintyEngine
from .memory_manager import LeoAdaptiveMemory
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV15Response, SystemStatus, BeliefDistribution, CalibrationMetrics
)

class LeoV15Orchestrator:
    """
    SYSTEM: HYPER RISK-BOUNDED EPISTEMIC CORE v15.0
    Objective: Near-zero error via calibrated, shift-adaptive uncertainty.
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
        self.belief_engine = BeliefEngine()
        self.calibration_engine = CalibrationEngine()
        self.meta_uncertainty_engine = MetaUncertaintyEngine()
        self.memory = LeoAdaptiveMemory()
        self.max_iters = 3

    async def run(self, user_input: str) -> LeoV15Response:
        # 12) MEMORY SYSTEM
        if user_input in self.l1_cache:
            belief = self.belief_engine.calculate_belief([], 1.0)
            return self._commit_response(self.l1_cache[user_input], 0.0, belief, 1.0, None, ["Verified L1 Hit"])

        # 2) SPEC EXTRACTION
        spec, clarifications = await self.spec_constructor.construct(user_input)
        if not spec:
            return self._abstain_response("Incomplete spec or out-of-domain", clarifications)

        # 11) ANYTIME REASONING
        for iteration in range(self.max_iters):
            # 3) MULTI-EVIDENCE GENERATION
            paths = await self.reasoning_engine.execute_paths(spec, "HIGH")
            
            # 4) DEPENDENCY CONTROL
            relationship = self.dependency_tracker.classify_cluster([p.path_id for p in paths])
            agreement_level, conflict_detected = self.fusion_engine.fuse(paths, relationship)
            
            # 7) CALIBRATION LAYER & 8) META-UNCERTAINTY
            agent_confidences = [p.confidence for p in paths]
            meta_u_detected = self.meta_uncertainty_engine.check_meta_uncertainty(agent_confidences)
            
            # 6) RETRIEVAL VALIDATION
            r_success, r_agreement, r_conflicts = await self.retrieval_validator.validate(user_input, paths[0].output)
            
            # 13) DRIFT + INVARIANT MONITORING
            v_results = await asyncio.gather(*[self.formal_verifier.verify(p.output, spec) for p in paths])
            v_pass_rate = sum(1 for r in v_results if r[0]) / len(paths)
            cal_metrics = self.calibration_engine.validate_calibration(agent_confidences, [r[0] for r in v_results])
            
            # 9) RISK ESTIMATION
            confidence = (agreement_level * 0.4) + (v_pass_rate * 0.4) + (r_agreement * 0.2)
            risk_val = self.risk_engine.calculate_risk(paths, confidence).risk_level
            risk_val = self.calibration_engine.adjust_risk(risk_val)
            
            # 5) KNOWLEDGE MODEL (Belief)
            belief_dist = self.belief_engine.calculate_belief(paths, v_pass_rate)
            
            # 10) COMMIT / ABSTAIN GATE
            if risk_val <= self.risk_engine.risk_threshold and not conflict_detected and cal_metrics.is_stable and not meta_u_detected:
                # COMMIT
                best_solution = paths[0]
                self.l1_cache[user_input] = best_solution.output
                return self._commit_response(best_solution.output, risk_val, belief_dist, confidence, cal_metrics, ["Calibration-certified consensus reached"])
            
            if iteration == self.max_iters - 1:
                # ABSTAIN
                reason = f"Risk ({risk_val:.3f}) exceeds bound or Calibration unstable ({cal_metrics.is_stable}). Meta-U: {meta_u_detected}"
                return self._abstain_response(reason, ["Failure to stabilize calibrated uncertainty under shift."])

        return self._abstain_response("Max iterations reached without calibration commitment.", [])

    def _commit_response(self, answer: Any, risk: float, belief: BeliefDistribution, confidence: float, cal: CalibrationMetrics, summary: List[str]) -> LeoV15Response:
        return LeoV15Response(
            status=SystemStatus.SUCCESS,
            risk_bound=risk,
            belief_distribution=belief,
            calibration_metrics=cal,
            confidence=confidence * 100,
            verified=True,
            summary=summary
        )

    def _abstain_response(self, reason: str, risks: List[str]) -> LeoV15Response:
        return LeoV15Response(
            status=SystemStatus.UNCERTAIN,
            risk_bound=1.0,
            confidence=0.0,
            verified=False,
            summary=["System ABSTAINED for Calibration Integrity."],
            reason=reason,
            risks=risks,
            escalation_needed=True
        )

