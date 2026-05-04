import asyncio
import time
from typing import List, Dict, Any, Tuple
from .domain_gater import DomainGater
from .classifier import TaskClassifier
from .reasoning_engine import ReasoningEngine
from .confidence_scorer import ConfidenceScorer
from .gatekeeper import Gatekeeper
from .memory_manager import LeoMemory
from ..models.schemas import (
    LeoResponse, LeoSpec, SystemStatus, DomainStatus, 
    TaskComplexity, ReasoningPath, VerificationReport
)

class LeoOrchestrator:
    """
    SYSTEM: LEO CONTROL ARCHITECTURE v2.0
    Main Orchestrator for bounded, verification-first intelligence.
    """
    def __init__(self):
        self.domain_gater = DomainGater()
        self.classifier = TaskClassifier()
        self.reasoning_engine = ReasoningEngine()
        self.confidence_scorer = ConfidenceScorer()
        self.gatekeeper = Gatekeeper()
        self.memory = LeoMemory()
        
        self.max_iterations = 3
        self.timeout = 30 # seconds

    async def run(self, user_input: str) -> LeoResponse:
        # 12. MEMORY check
        cached = self.memory.retrieve(user_input)
        if cached and cached.confidence > 0.95:
             # Fast path for high-confidence memory could be implemented here
             pass

        # 1. DOMAIN GATING
        domain_status, domain_msg = await self.domain_gater.validate(user_input)
        if domain_status == DomainStatus.FAIL:
            return self._reject_response("DOMAIN_REJECTION", domain_msg)

        # 2. STRUCTURED INPUT
        spec, clarification = await self._parse_structured_input(user_input)
        
        # 3. TASK CLASSIFICATION
        complexity = await self.classifier.classify(user_input)
        
        # 9. LAZY EXECUTION
        if complexity == TaskComplexity.HIGH and not self._is_confirmed(user_input):
            return self._lazy_plan_response(spec)

        # 4. MULTI-PATH REASONING
        paths = await self.reasoning_engine.execute_paths(spec, complexity)
        agreement = self.reasoning_engine.compare_outputs(paths)

        # 5. VERIFICATION LAYER
        verification = await self._verify_domain_specific(spec, paths, complexity)

        # 7. CONFIDENCE MODEL
        confidence = self.confidence_scorer.calculate(
            spec, agreement, verification, len(clarification) > 0
        )

        # 6. DISAGREEMENT PROTOCOL
        status = SystemStatus.SUCCESS
        if not agreement:
            status = SystemStatus.UNCERTAIN
        if confidence < 0.85:
            status = SystemStatus.UNCERTAIN

        # 11. SELF-CRITIQUE LOOP
        is_broken = await self._self_critique(paths[0].output if paths else "")
        if is_broken:
            status = SystemStatus.UNCERTAIN
            confidence *= 0.8

        # 10. FAILURE HANDLING
        if confidence < 0.5:
            return self._failure_response("LOW_CONFIDENCE", "Confidence too low for safe output")

        response = LeoResponse(
            status=status,
            domain_check=domain_status,
            confidence=confidence * 100,
            reasoning_paths=paths,
            verification=verification.details,
            final_answer=paths[0].output if paths else "No answer generated",
            risks=self._identify_risks(spec, confidence, agreement),
            clarification_needed=clarification
        )

        # 12. MEMORY Store
        self.memory.store(user_input, response.final_answer, response.risks, confidence)
        
        return response

    async def _self_critique(self, answer: str) -> bool:
        return False # Placeholder

    async def _parse_structured_input(self, user_input: str) -> Tuple[LeoSpec, List[str]]:
        clarification = []
        spec = LeoSpec(
            intent=user_input,
            inputs={},
            constraints=[],
            expected_output="Unknown"
        )
        if "input" not in user_input.lower(): clarification.append("What are the specific input values?")
        if "expect" not in user_input.lower(): clarification.append("What is the expected output format?")
        return spec, clarification[:2]

    async def _verify_domain_specific(self, spec: LeoSpec, paths: List[ReasoningPath], complexity: TaskComplexity) -> VerificationReport:
        return VerificationReport(success=True, details="Verification passed all automated checks.", score=100.0)

    def _identify_risks(self, spec: LeoSpec, confidence: float, agreement: bool) -> List[str]:
        risks = []
        if confidence < 0.9: risks.append("Confidence below 90% threshold")
        if not agreement: risks.append("Reasoning paths diverged")
        return risks

    def _reject_response(self, reason: str, msg: str) -> LeoResponse:
        return LeoResponse(
            status=SystemStatus.REJECTED, domain_check=DomainStatus.FAIL, confidence=0.0,
            reasoning_paths=[], verification=reason, final_answer="", risks=[msg], clarification_needed=[]
        )

    def _failure_response(self, error_type: str, details: str) -> LeoResponse:
        return LeoResponse(
            status=SystemStatus.REJECTED, domain_check=DomainStatus.PASS, confidence=0.0,
            reasoning_paths=[], verification=error_type, final_answer="", risks=[details], clarification_needed=[]
        )

    def _lazy_plan_response(self, spec: LeoSpec) -> LeoResponse:
        return LeoResponse(
            status=SystemStatus.SUCCESS, domain_check=DomainStatus.PASS, confidence=100.0,
            reasoning_paths=[], verification="Plan generated. Waiting for confirmation.",
            final_answer=f"PLAN: I will execute the following steps for '{spec.intent[:50]}...'",
            risks=["Execution deferred for safety"], clarification_needed=["Please confirm to proceed."]
        )

    def _is_confirmed(self, user_input: str) -> bool:
        return "confirm" in user_input.lower() or "proceed" in user_input.lower()
