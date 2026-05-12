import math
from typing import Dict, Any

class QueryIntelligence:
    """
    Layer 0: Query Intelligence Engine
    Detects query type, complexity, novelty, and entropy.
    """
    def __init__(self):
        self.categories = {
            "math": ["calculate", "integral", "derivative", "solve", "math", "equation"],
            "code": ["write a function", "python", "javascript", "rust", "debug", "code"],
            "fact": ["who is", "what is the capital", "when did"],
            "reasoning": ["why", "how to", "explain", "compare"]
        }

    def _calculate_entropy(self, text: str) -> float:
        if not text: return 0.0
        prob = [text.count(c) / len(text) for c in set(text)]
        return -sum(p * math.log2(p) for p in prob)

    def analyze(self, query: str) -> Dict[str, Any]:
        q_lower = query.lower()
        entropy = self._calculate_entropy(query)
        length = len(query)
        
        # Determine Query Type
        q_type = "GENERAL"
        for cat, keywords in self.categories.items():
            if any(k in q_lower for k in keywords):
                q_type = cat.upper()
                break
        
        # Scoring
        complexity = min(10, (length / 50) + (entropy / 2))
        novelty = entropy * (length / 100)
        
        # Classification
        if length < 30 and entropy < 3.5:
            classification = "SIMPLE"
        elif q_type in ["MATH", "CODE"]:
            classification = "TOOL"
        elif entropy > 4.5 or length > 300:
            classification = "COMPLEX"
        else:
            classification = "RETRIEVAL"

        return {
            "type": q_type,
            "classification": classification,
            "complexity": round(complexity, 2),
            "novelty": round(novelty, 2),
            "entropy": round(entropy, 2)
        }

if __name__ == "__main__":
    qi = QueryIntelligence()
    print(qi.analyze("What is the capital of France?"))
    print(qi.analyze("Calculate the area of a circle with radius 5."))
