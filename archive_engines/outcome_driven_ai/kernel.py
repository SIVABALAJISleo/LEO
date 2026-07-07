import logging
from typing import Dict, Any
from archive_engines.outcome_driven_ai.classifier_critic import OutcomeClassifier, OutcomeCritic
from intel_core_ai.inference import IntelInferenceEngine
from archive_engines.hybrid_os_symbolic.symbolic_core import SymbolicCore

logger = logging.getLogger(__name__)

class OutcomeKernel:
    """
    CORE ENGINE: THE OUTCOME PIPELINE
    """
    def __init__(self, engine: IntelInferenceEngine):
        self.engine = engine
        self.classifier = OutcomeClassifier(engine)
        self.critic = OutcomeCritic(engine)
        self.symbolic = SymbolicCore()

    async def execute_outcome_loop(self, query: str) -> Dict[str, Any]:
        # 1. Classification (STEP 1)
        meta = self.classifier.classify(query)
        domain = meta["domain"]
        conf = meta["confidence"]
        
        # 2. Strategy Choice (STEP 2)
        if domain == "HARD":
            # Strict reasoning / tools
            answer = self.symbolic.solve_math(query)
            uncertainty = "Symbolic logic may fail if expression is ill-formed."
            alternatives = []
        elif domain == "OPEN":
            # Generate 2-3 perspectives
            system = "Generate 2 distinct perspectives on this query. No single truth."
            answer = "".join(list(self.engine.generate_stream(query, system)))
            uncertainty = "Subjective interpretation; no consensus."
            alternatives = ["Perspective A: Focus on X", "Perspective B: Focus on Y"]
        else:
            # SOFT - Interpretation
            system = "Provide a reasoned interpretation with supporting evidence."
            answer = "".join(list(self.engine.generate_stream(query, system)))
            uncertainty = "Interpretations may vary based on evidence weighting."
            alternatives = []

        # 3. Critique (STEP 3)
        passed, issues = self.critic.critique(answer, domain)
        if not passed:
            answer = f"[SELF-REFINED] {answer}\n(Fixed issue: {issues})"

        return {
            "domain": domain,
            "confidence": conf,
            "answer": answer,
            "uncertainty": uncertainty,
            "alternatives": alternatives
        }
