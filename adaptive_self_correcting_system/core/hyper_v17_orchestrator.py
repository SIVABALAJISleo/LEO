import asyncio
from typing import List, Dict, Any, Tuple, Optional
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
from .consequence_engine import ConsequenceEngine
from .uncertainty_engine import UncertaintyEngine
from ..models.schemas import (
    LeoV17Response, SystemStatus, UncertaintyLevel, RecommendedAction, ConsequenceLevel
)

class LeoV17Orchestrator:
    """
    SYSTEM: HYPER UNCERTAINTY-CONTROL CORE v17.0
    Objective: Optimize for SAFE DECISIONS using bounded uncertainty.
    """
    def __init__(self, risk_threshold: float = 0.05):
        self.spec_constructor = SpecConstructor()
        self.formal_verifier = FormalVerifier()
        self.reasoning_engine = ReasoningEngine()
        self.retrieval_validator = RetrievalValidator()
        self.fusion_engine = AdvancedFusionEngine()
        self.dependency_tracker = DependencyTracker()
        self.drift_controller = DriftController()
        self.risk_engine = RiskEngine(risk_threshold=risk_threshold)
        self.meta_uncertainty_engine = MetaUncertaintyEngine()
        self.consequence_engine = ConsequenceEngine()
        self.uncertainty_engine = UncertaintyEngine()

    async def run(self, user_input: str) -> LeoV17Response:
        # 1) INPUT ANALYSIS
        c_level, reversibility = self.consequence_engine.classify(user_input)
        
        # 2) IRREVERSIBILITY GATE
        # (Already handled in classification)

        spec, _ = await self.spec_constructor.construct(user_input)
        if not spec:
            return LeoV17Response(
                confidence=0.0,
                uncertainty_level=UncertaintyLevel.HIGH,
                uncertainty_reason="Incomplete spec.",
                consequence_level=c_level,
                recommended_action=RecommendedAction.BLOCK_AND_ESCALATE
            )

        # 3) MULTI-EVIDENCE GENERATION
        paths = await self.reasoning_engine.execute_paths(spec, "HIGH")
        
        # 4) ORTHOGONAL VALIDATION
        relationship = self.dependency_tracker.classify_cluster([p.path_id for p in paths])
        agreement_level, conflict_detected = self.fusion_engine.fuse(paths, relationship)
        
        v_results = await asyncio.gather(*[self.formal_verifier.verify(p.output, spec) for p in paths])
        v_pass_rate = sum(1 for r in v_results if r[0]) / len(paths)
        
        meta_u_detected = self.meta_uncertainty_engine.check_meta_uncertainty([p.confidence for p in paths])
        
        # 5) UNCERTAINTY ESTIMATION
        # confidence = agreement + verification + retrieval (simplified)
        confidence = (agreement_level * 0.5) + (v_pass_rate * 0.5)
        
        u_level, u_reason, r_action = self.uncertainty_engine.estimate(confidence, conflict_detected, meta_u_detected)
        
        # 7) DECISION CONTROL (CRITICAL)
        # Translation of uncertainty into action is handled by the engine mapping
        
        return LeoV17Response(
            answer=paths[0].output if r_action != RecommendedAction.BLOCK_AND_ESCALATE else None,
            confidence=confidence * 100,
            uncertainty_level=u_level,
            uncertainty_reason=u_reason,
            consequence_level=c_level,
            recommended_action=r_action
        )
吐
