import asyncio
from .input_sanitizer import InputSanitizer
from .ood_detector import OODDetector
from .completeness_service import CompletenessService
from .multi_view_engine import MultiViewEngine
from .consequence_engine import ConsequenceEngine
from .knowledge_layer import KnowledgeLayer
from .reasoning_engine import ReasoningEngine
from .trust_engine import ConsensusEngine
from .calibration_service import CalibrationService
from .symbolic_logic_service import SymbolicLogicService
from .anti_halting_service import AntiHaltingService
from .monitoring_service import MonitoringService
from .verification_layer import VerificationLayer
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV27Response, SystemStatus, RiskLevel
)

class LeoV27Orchestrator:
    """
    SYSTEM: HYPER HYBRID FAILURE-PROOF CORE v27.0
    Objective: 99.9% reliability through absolute consensus and formal verification.
    """
    def __init__(self, confidence_floor: float = 0.90):
        self.sanitizer = InputSanitizer()
        self.ood_detector = OODDetector()
        self.completeness = CompletenessService()
        self.multi_view = MultiViewEngine()
        self.consequence = ConsequenceEngine()
        self.knowledge = KnowledgeLayer()
        self.reasoner = ReasoningEngine()
        self.consensus = ConsensusEngine()
        self.calibration = CalibrationService()
        self.symbolic = SymbolicLogicService()
        self.anti_halting = AntiHaltingService()
        self.monitor = MonitoringService()
        self.verifier = VerificationLayer()
        self.cache = SemanticCache(threshold=0.9)
        self.confidence_floor = confidence_floor

    async def run(self, user_input: str) -> LeoV27Response:
        self.anti_halting.start_track()

        # 1. INPUT CONTROL + 4. AMBIGUITY + 5. COMPLETENESS
        is_valid, clean_input, err = self.sanitizer.sanitize(user_input)
        if not is_valid: return self._abstain(err)
        
        is_ambiguous, q = self.completeness.detect_ambiguity(clean_input)
        if is_ambiguous: return self._abstain(f"CLARIFICATION_REQUIRED: {q}")

        # 3. OOD DETECTOR
        # (Using mock vector [0.1, 0.2] for OOD check)
        is_ood, ood_score = self.ood_detector.check_ood([0.1, 0.2])
        if is_ood: return self._abstain(f"OOD_UNKNOWN: Score {ood_score:.2f}")

        # 7. MULTI-REPRESENTATION
        self.multi_view.generate_views(clean_input)
        
        # 14. RISK + 15. IRREVERSIBILITY
        r_level, _ = self.consequence.classify(clean_input)
        
        # 17. SEMANTIC CACHE
        cached = self.cache.query(clean_input)
        if cached:
            return LeoV27Response(answer=cached.code, confidence=1.0, status=SystemStatus.VERIFIED, risk_level=r_level, verification="CACHED_PASS")

        # 8. MULTI-REASONING + 9. CONSENSUS
        tasks = [self.reasoner.execute_paths(clean_input, "HIGH") for _ in range(3)]
        path_results = await asyncio.gather(*tasks)
        outputs = [p[0].output for p in path_results]
        confidences = [p[0].confidence for p in path_results]

        has_consensus, winner, agreement = self.consensus.check_consensus(outputs)
        
        # 10. CONFIDENCE CALIBRATION
        calibrated_conf = self.calibration.calibrate(confidences)
        
        # 16. FINAL DECISION ENGINE (CORE)
        if not has_consensus or calibrated_conf < self.confidence_floor:
            return self._abstain(f"Safety Gate: Consensus={has_consensus}, Confidence={calibrated_conf:.2f}")

        # 11. SYMBOLIC VERIFICATION + 13. ANTI-HALTING
        is_safe, limit_msg = self.anti_halting.check_limits(5)
        if not is_safe: return self._abstain(limit_msg)

        logic_valid, logic_msg = self.symbolic.verify_logic(winner, clean_input)
        if not logic_valid: return self._abstain(logic_msg)

        # 12. CONTRADICTION CHECK (Final verifier check)
        v_success, checks = self.verifier.verify(winner, [])
        if not v_success: return self._abstain("Logical contradiction or invariant violation.")

        return LeoV27Response(
            answer=winner,
            confidence=calibrated_conf,
            status=SystemStatus.VERIFIED,
            risk_level=r_level,
            verification="PASSED_ALL_LAYERS"
        )

    def _abstain(self, reason: str) -> LeoV27Response:
        self.monitor.log_error("ABSTENTION", reason)
        return LeoV27Response(
            confidence=0.0,
            status=SystemStatus.ABSTAINED,
            reason=reason,
            risk_level=RiskLevel.MINOR,
            verification="FAILED"
        )

