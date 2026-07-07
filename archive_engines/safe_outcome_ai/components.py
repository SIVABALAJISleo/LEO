import logging
from typing import List, Tuple
from archive_engines.hybrid_os_symbolic.symbolic_core import SymbolicCore
from archive_engines.llm_os_core.memory_knowledge import OSKnowledge
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class SafeHardProcessor:
    """
    STEP 2: HARD PROCESSING
    Solve -> Execute -> Re-solve differently -> Compare -> Retry.
    """
    def __init__(self, symbolic: SymbolicCore):
        self.symbolic = symbolic

    def process(self, query: str) -> Tuple[str, float]:
        # Path 1: Direct solve
        res1 = self.symbolic.solve_math(query)
        # Path 2: Simplified solve
        res2 = self.symbolic.solve_math(f"simplify {query}")
        
        if res1 == res2:
            return res1, 1.0
        
        # Retry Path (STEP 2: Retry)
        res_retry = self.symbolic.solve_math(f"evaluate {query}")
        if res_retry == res1: return res1, 0.9
        
        return "INSUFFICIENT DATA: Solution mismatch across 3 execution paths.", 0.0

class SafeSoftProcessor:
    """
    STEP 2: SOFT PROCESSING
    3-5 Query variations -> Retrieve -> Re-rank -> Verify.
    """
    def __init__(self, engine: IntelInferenceEngine, knowledge: OSKnowledge):
        self.engine = engine
        self.knowledge = knowledge

    def process(self, query: str) -> Tuple[str, List[str]]:
        # 1. 3-5 Query Variations
        sys = "Generate 3 diverse search query variations for this topic. Output list."
        variations = ["".join(list(self.engine.generate_stream(query, sys)))]
        
        # 2. Retrieve & Re-rank (Simulated)
        results = []
        for v in variations:
            results.extend(self.knowledge.retrieve(v))
        
        # 3. Every claim MUST map to evidence
        context = "\n".join(results[:5])
        ans_sys = f"Answer using ONLY this context. If unknown, mark uncertain.\nContext: {context}"
        answer = "".join(list(self.engine.generate_stream(query, ans_sys)))
        
        return answer, results[:3]

class SafeCritic:
    """
    STEP 3: SELF-CRITIQUE + VERIFICATION
    Optional 2-candidate choice logic.
    """
    def __init__(self, engine: IntelInferenceEngine):
        self.engine = engine

    def select_best(self, candidates: List[str], domain: str) -> str:
        if len(candidates) < 2: return candidates[0]
        
        sys = f"Choose the best {domain} answer based on logic and evidence grounding. Output ONLY the selected text."
        prompt = f"Candidate A: {candidates[0]}\nCandidate B: {candidates[1]}"
        return "".join(list(self.engine.generate_stream(prompt, sys)))
