import logging
from typing import Dict, Any, Tuple
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class HyperCritique:
    """
    LAYER 7: ERROR CONTROL SYSTEM
    Critiques and assigns confidence scores to outputs.
    """
    def __init__(self, inference: IntelInferenceEngine):
        self.inference = inference

    def critique(self, answer: str, context: str) -> Tuple[float, str]:
        """
        Self-check: critique the answer against context.
        """
        system_prompt = (
            "Critique this answer for accuracy and grounding. Output ONLY JSON.\n"
            "Format: {\"confidence\": 0.0-1.0, \"issues\": \"...\", \"is_hallucination\": bool}\n"
            f"Context: {context}"
        )
        gen = self.inference.generate_stream(answer, system_prompt)
        res = "".join(list(gen))
        try:
            data = json.loads(res[res.find("{"):res.rfind("}")+1])
            return data.get("confidence", 0.5), data.get("issues", "No issues identified.")
        except:
            return 0.5, "Critique failed."

class HyperLearning:
    """
    LAYER 9: BEHAVIORAL LEARNING
    Tracks patterns to update a lightweight profile.
    """
    def __init__(self):
        self.profile: Dict[str, Any] = {"total_queries": 0, "corrections": 0}

    def record_interaction(self, was_corrected: bool):
        self.profile["total_queries"] += 1
        if was_corrected:
            self.profile["corrections"] += 1
        logger.info(f"Behavioral Update: Profile now has {self.profile['total_queries']} entries.")
