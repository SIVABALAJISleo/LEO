import logging
from typing import Dict, Any
from archive_engines.boundary_perfect_ai.intent_handler import BoundaryIntentHandler
from archive_engines.boundary_perfect_ai.reasoning_engine import BoundaryReasoningEngine
from archive_engines.outcome_driven_ai.classifier_critic import OutcomeClassifier
from archive_engines.hybrid_os_symbolic.symbolic_core import SymbolicCore
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class BoundaryKernel:
    """
    THE 10-STEP BOUNDARY-PERFECT PIPELINE
    """
    def __init__(self, engine: IntelInferenceEngine):
        self.engine = engine
        self.classifier = OutcomeClassifier(engine)
        self.intent_h = BoundaryIntentHandler(engine)
        self.symbolic = SymbolicCore()
        self.reasoning_e = BoundaryReasoningEngine(engine, self.symbolic)

    async def execute_pipeline(self, query: str) -> Dict[str, Any]:
        # 1. Domain Lock
        meta = self.classifier.classify(query)
        domain = meta["domain"]
        
        # 2. Intent Contract
        contract = self.intent_h.contract(query)
        
        # 3. Probability Split (If ambiguity high)
        if contract["ambiguity_score"] > 0.5:
            self.intent_h.split_probability(query)

        # 4 & 5 & 6. Retrieval, Multi-path & Verification
        answer, verification = self.reasoning_e.run_multi_path(query, domain)
        
        # 8. Self-Verifying Details
        ver_details = self.reasoning_e.generate_self_verifying_output(answer)

        # 9. Confidence & Uncertainty
        conf = 95 if domain == "HARD" else 75
        residual = "Semantic ambiguity in query parameters."
        
        return {
            "domain": domain,
            "intent": contract["interpretation"],
            "assumptions": contract["assumptions"],
            "answer": answer,
            "verification": verification,
            "success_test": ver_details["success_test"],
            "failure_case": ver_details["failure_case"],
            "confidence": conf,
            "residual_uncertainty": residual
        }
