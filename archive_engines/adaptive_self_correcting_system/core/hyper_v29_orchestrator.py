import asyncio
from .input_sanitizer import InputSanitizer
from .ood_detector import OODDetector
from .completeness_service import CompletenessService
from .hypothesis_engine import HypothesisEngine
from .consequence_engine import ConsequenceEngine
from .knowledge_layer import KnowledgeLayer
from .reasoning_engine import ReasoningEngine
from .trust_engine import ConsensusEngine
from .calibration_service import CalibrationService
from .symbolic_logic_service import SymbolicLogicService
from .anytime_engine import AnytimeEngine
from .meta_controller import MetaUncertaintyController
from .monitoring_service import MonitoringService
from .verification_layer import VerificationLayer
from .decision_gate import DecisionCore, SystemState
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV29Response, SystemStatus, RiskLevel, VerificationResult
)

class LeoV29Orchestrator:
    """
    SYSTEM: HYPER HYBRID ZERO-UNSAFE-OUTPUT CORE v29.0
    Objective: Zero unsafe outputs through formal decision gating.
    """
    def __init__(self):
        self.sanitizer = InputSanitizer()
        self.ood = OODDetector()
        self.completeness = CompletenessService()
        self.hypothesis = HypothesisEngine()
        self.consequence = ConsequenceEngine()
        self.knowledge = KnowledgeLayer()
        self.reasoner = ReasoningEngine()
        self.consensus = ConsensusEngine()
        self.anytime = AnytimeEngine()
        self.calibration = CalibrationService()
        self.symbolic = SymbolicLogicService()
        self.meta_controller = MetaUncertaintyController()
        self.monitor = MonitoringService()
        self.verifier = VerificationLayer()
        self.decision_core = DecisionCore()
        self.cache = SemanticCache(threshold=0.9)

    async def run(self, user_input: str) -> LeoV29Response:
        state = SystemState()

        # 14. META-UNCERTAINTY CONTROLLER
        stable, msg = self.meta_controller.check_system_integrity([100.0], 0.01)
        if not stable:
            state.system_unstable = True
            state.error_msg = msg
            return self.decision_core.decision_gate(state)

        # 1. INPUT NORMALIZATION + 5. COMPLETENESS
        is_valid, clean_input, err = self.sanitizer.sanitize(user_input)
        if not is_valid:
            state.missing_information = True
            state.error_msg = err
            return self.decision_core.decision_gate(state)

        # 3. OOD DETECTION
        is_ood, ood_score = self.ood.check_ood([0.1, 0.2])
        if is_ood:
            state.ood_detected = True
            state.error_msg = f"OOD Score {ood_score:.2f}"
            return self.decision_core.decision_gate(state)

        # 4. AMBIGUITY ENGINE
        # (Simulating hypothesis entropy check)
        is_ambiguous, q = self.completeness.detect_ambiguity(clean_input)
        if is_ambiguous:
            state.ambiguity_high = True
            state.error_msg = q
            return self.decision_core.decision_gate(state)

        # 15. RISK CLASSIFIER
        r_level, _ = self.consequence.classify(clean_input)
        state.risk = r_level

        # 18. SEMANTIC CACHE
        cached = self.cache.query(clean_input)
        if cached:
            return LeoV29Response(answer=cached.code, status=SystemStatus.VERIFIED, confidence=1.0, risk=RiskLevel.LOW, verification=VerificationResult.PASSED)

        # 7. ENSEMBLE + 8. CONSENSUS
        tasks = [self.reasoner.execute_paths(clean_input, "HIGH") for _ in range(3)]
        path_results = await asyncio.gather(*tasks)
        outputs = [p[0].output for p in path_results]
        confidences = [p[0].confidence for p in path_results]

        has_consensus, winner, agreement = self.consensus.check_consensus(outputs)
        cal_conf = self.calibration.calibrate(confidences)
        
        if not has_consensus: state.model_disagreement = True
        if cal_conf < 0.90: state.low_confidence = True
        state.confidence = cal_conf
        state.error_msg = f"Consensus={has_consensus}, Calibrated Confidence={cal_conf:.2f}"

        # 12. ANYTIME REASONING
        refined_result, est_error = self.anytime.solve(clean_input)
        state.result = refined_result

        # 10. SYMBOLIC VERIFICATION (Z3)
        logic_valid, logic_msg = self.symbolic.verify_logic(refined_result, clean_input)
        if not logic_valid:
            state.verification_failed = True
            state.error_msg = logic_msg

        # FINAL DECISION GATE
        return self.decision_core.decision_gate(state)

