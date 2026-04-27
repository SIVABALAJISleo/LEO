import logging
from typing import Dict, Any, List, Tuple
from hybrid_os_symbolic.symbolic_core import SymbolicCore
from llm_os_core.memory_knowledge import OSKnowledge
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class HardProcessor:
    """
    STEP 2: HARD PROCESSING
    Solve -> Re-solve differently -> Compare.
    """
    def __init__(self, symbolic: SymbolicCore):
        self.symbolic = symbolic

    def process(self, query: str) -> Tuple[str, float]:
        # Solve 1
        res1 = self.symbolic.solve_math(query)
        # Solve 2 (Simulated different path)
        res2 = self.symbolic.solve_math(query + " # simplified")
        
        if res1 == res2:
            return res1, 1.0
        return f"Mismatch detected: {res1} vs {res2}. Failing safely.", 0.0

class SoftProcessor:
    """
    STEP 2: SOFT PROCESSING
    Query -> Retrieve -> Re-rank -> Verify.
    """
    def __init__(self, engine: IntelInferenceEngine, knowledge: OSKnowledge):
        self.engine = engine
        self.knowledge = knowledge

    def process(self, query: str) -> Tuple[str, List[str]]:
        # 1. Generate 3-5 search queries
        queries = ["".join(list(self.engine.generate_stream(query, "Gen 3 search queries for this.")))]
        
        # 2. Retrieve & Re-rank
        all_results = []
        for q in queries[:3]:
            all_results.extend(self.knowledge.retrieve(q))
            
        # 3. Verify
        context = "\n".join(all_results[:5])
        answer = "".join(list(self.engine.generate_stream(query, f"Answer using ONLY this context: {context}")))
        return answer, all_results[:3]
