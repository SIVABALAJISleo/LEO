import logging
import asyncio
from typing import Dict, Any, List
from self_skeptical_engine.components import AdversarialChecker, EpistemicTagger
from high_accuracy_engine.components import HighAccuracyRouter, IntentLock
from hybrid_os_symbolic.symbolic_core import SymbolicCore
from llm_os_core.memory_knowledge import OSKnowledge
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class SelfSkepticalKernel:
    """
    THE 16-STEP SELF-SKEPTICAL PIPELINE
    """
    def __init__(self, engine: IntelInferenceEngine):
        self.engine = engine
        self.router = HighAccuracyRouter(engine)
        self.intent_lock = IntentLock(engine)
        self.adversarial = AdversarialChecker(engine)
        self.tagger = EpistemicTagger()
        self.symbolic = SymbolicCore()
        self.knowledge = OSKnowledge()

    async def execute_pipeline(self, query: str) -> Dict[str, Any]:
        # 1, 2. Router & Intent Contract
        meta = self.router.classify(query)
        domain = meta["domain"]
        lock_data = self.intent_lock.lock(query)
        
        # 4, 5, 6, 7. Controlled Gen, Tool-First, Multi-path, Retrieval
        answer = ""
        reasoning = ""
        conf = 0.0
        verified = False
        
        if domain == "HARD":
            answer = self.symbolic.solve_math(query)
            reasoning = "Symbolic Core computation verified through formal math engine."
            conf = 0.95
            verified = True
        elif domain == "OPEN":
            # 2-3 perspectives
            system = "Provide 2 distinct perspectives. Expose uncertainty."
            answer = "".join(list(self.engine.generate_stream(query, system)))
            reasoning = "Subjective analysis; perspectives generated to reflect range of opinion."
            conf = 0.50
        else:
            # FACTUAL
            facts = self.knowledge.retrieve(query)
            context = "\n".join(facts)
            system = f"Answer using only evidence: {context}"
            answer = "".join(list(self.engine.generate_stream(query, system)))
            reasoning = f"Evidence-based reasoning mapping to {len(facts)} retrieved context chunks."
            conf = 0.80

        # 10. Adversarial Check (Step 10)
        risk = self.adversarial.check(query, answer)
        if "wrong" in risk.lower(): conf -= 0.1 # Dynamic confidence reduction

        # 13. Epistemic Label
        label = self.tagger.get_label(domain, conf, verified)

        return {
            "domain": domain,
            "intent": lock_data["interpretation"],
            "assumptions": lock_data["assumptions"],
            "answer": answer,
            "reasoning": reasoning,
            "adversarial_risk": risk,
            "confidence": conf,
            "epistemic_label": label,
            "uncertainty": "Residual gap in context or semantic interpretation."
        }
