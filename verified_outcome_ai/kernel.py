import logging
import json
from typing import Dict, Any, Tuple
from verified_outcome_ai.processors import HardProcessor, SoftProcessor
from outcome_driven_ai.classifier_critic import OutcomeClassifier, OutcomeCritic
from hybrid_os_symbolic.symbolic_core import SymbolicCore
from llm_os_core.memory_knowledge import OSKnowledge
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class VerifiedKernel:
    """
    CORE: THE VERIFIED OUTCOME PIPELINE
    """
    def __init__(self, engine: IntelInferenceEngine):
        self.engine = engine
        self.classifier = OutcomeClassifier(engine)
        self.critic = OutcomeCritic(engine)
        self.symbolic = SymbolicCore()
        self.knowledge = OSKnowledge()
        
        self.hard_p = HardProcessor(self.symbolic)
        self.soft_p = SoftProcessor(engine, self.knowledge)

    async def execute_verified_loop(self, query: str) -> Dict[str, Any]:
        # 1. Classification (STEP 1)
        meta = self.classifier.classify(query)
        domain = meta["domain"]
        conf = meta["confidence"]
        
        # 2. Confidence Check & Domain Choice
        # If low confidence, we choose the safer path or SOFT
        if conf < 0.7:
             domain = "SOFT" # Default safer path

        # 3. Processing (STEP 2)
        sources = []
        alternatives = []
        if domain == "HARD":
            answer, p_conf = self.hard_p.process(query)
            uncertainty = "Symbolic logic mismatch" if p_conf == 0 else "None"
        elif domain == "OPEN":
            # Generate 2-3 structured perspectives
            system = "Generate 3 distinct perspectives on this topic. Format as options."
            answer = "".join(list(self.engine.generate_stream(query, system)))
            uncertainty = "Subjective; no singular truth."
            alternatives = ["Perspective 1", "Perspective 2", "Perspective 3"]
        else:
            # SOFT
            answer, sources = self.soft_p.process(query)
            uncertainty = "Limited evidence in local store." if not sources else "Interpretation variance."

        # 4. Self-Critique (STEP 3)
        passed, issues = self.critic.critique(answer, domain)
        if not passed:
            answer = f"[VERIFIED REFINEMENT] {answer}"

        return {
            "domain": domain,
            "confidence": conf,
            "answer": answer,
            "uncertainty": uncertainty,
            "alternatives": alternatives,
            "sources": sources
        }
