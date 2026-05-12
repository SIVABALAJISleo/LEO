import logging
import json
from typing import Dict, Any, Tuple
from safe_outcome_ai.components import SafeHardProcessor, SafeSoftProcessor, SafeCritic
from outcome_driven_ai.classifier_critic import OutcomeClassifier
from hybrid_os_symbolic.symbolic_core import SymbolicCore
from llm_os_core.memory_knowledge import OSKnowledge
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class SafeOutcomeKernel:
    """
    CORE ENGINE: THE SAFE OUTCOME PIPELINE
    """
    def __init__(self, engine: IntelInferenceEngine):
        self.engine = engine
        self.classifier = OutcomeClassifier(engine)
        self.critic = SafeCritic(engine)
        self.symbolic = SymbolicCore()
        self.knowledge = OSKnowledge()
        
        self.hard_p = SafeHardProcessor(self.symbolic)
        self.soft_p = SafeSoftProcessor(engine, self.knowledge)

    async def execute_safe_loop(self, query: str) -> Dict[str, Any]:
        # 1. Classification & Gating (STEP 1)
        meta = self.classifier.classify(query)
        domain = meta["domain"]
        conf = meta["confidence"]
        
        # 2. Confidence Gating (STEP 1)
        if conf < 0.7:
             domain = "SOFT" # Choose safer interpretation

        # 3. Processing (STEP 2)
        sources = []
        alternatives = []
        
        if domain == "HARD":
            # NEVER guess. Solve -> Re-solve -> Compare.
            answer, p_conf = self.hard_p.process(query)
            uncertainty = "Solution mismatch" if p_conf < 0.5 else "None"
        elif domain == "OPEN":
            # 2-3 structured perspectives
            system = "Generate 3 structured perspectives on this query. Optimize for usefulness."
            answer = "".join(list(self.engine.generate_stream(query, system)))
            uncertainty = "Subjective; multiple perspectives provided."
            alternatives = ["Perspective 1", "Perspective 2", "Perspective 3"]
        else:
            # SOFT
            # 2-candidate selection for safety (STEP 3)
            c1, sources = self.soft_p.process(query)
            c2, _ = self.soft_p.process(query)
            answer = self.critic.select_best([c1, c2], "SOFT")
            uncertainty = "Claims mapped to local evidence."

        return {
            "domain": domain,
            "confidence": conf,
            "answer": answer,
            "uncertainty": uncertainty,
            "alternatives": alternatives,
            "sources": sources
        }
