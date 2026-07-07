import logging
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class AdversarialChecker:
    """
    STEP 10: ADVERSARIAL CHECK
    Identifies why the answer could be wrong.
    """
    def __init__(self, engine: IntelInferenceEngine):
        self.engine = engine

    def check(self, query: str, answer: str) -> str:
        system = "What is the strongest reason this answer could be wrong or incomplete? Provide a concise critique."
        prompt = f"Query: {query}\nAnswer: {answer}"
        res = "".join(list(self.engine.generate_stream(prompt, system)))
        return res.strip()

class EpistemicTagger:
    """
    STEP 13: EPISTEMIC LABELING
    Tags output with [PROVEN], [INFERRED], etc.
    """
    def get_label(self, domain: str, conf: float, verification_passed: bool) -> str:
        if domain == "HARD" and verification_passed: return "PROVEN"
        if conf > 0.85: return "HIGH CONFIDENCE"
        if conf > 0.6: return "INFERRED"
        if conf > 0.3: return "UNCERTAIN"
        return "UNKNOWN"
