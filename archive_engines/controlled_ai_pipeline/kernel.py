import json
import logging
from typing import Dict, Any
from archive_engines.high_perf_intel_ai.inference import HighPerfEngine
from archive_engines.controlled_ai_pipeline.scorer import RubricEngine, Scorer
from archive_engines.hybrid_os_symbolic.symbolic_core import SymbolicCore
from archive_engines.llm_os_core.memory_knowledge import OSKnowledge

logger = logging.getLogger(__name__)

class ControlledKernel:
    """
    LAYER 11: CONTROL LOOP (MANDATORY)
    Orchestrates the measurable process pipeline.
    """
    def __init__(self, engine: HighPerfEngine, knowledge: OSKnowledge):
        self.engine = engine
        self.knowledge = knowledge
        self.rubric = RubricEngine()
        self.scorer = Scorer()
        self.symbolic = SymbolicCore()

    async def run_pipeline(self, query: str) -> Dict[str, Any]:
        # 1. Routing (LAYER 1)
        # Classify as DETERMINISTIC, FACTUAL, or OPEN-ENDED
        route_prompt = "Classify this query: DETERMINISTIC (math/logic), FACTUAL (RAG), or OPEN-ENDED. Output JSON: {\"class\": \"...\"}"
        res = "".join(list(self.engine.generate(query, route_prompt)))
        q_class = json.loads(res[res.find("{"):res.rfind("}")+1])["class"]

        # 2. Handle Deterministic
        if q_class == "DETERMINISTIC":
             # Route to SymPy/Z3
             return {"status": "SUCCESS", "mode": "SYMBOLIC", "result": self.symbolic.solve_math(query)}

        # 3. Handle Factual / Open-Ended (LAYER 3 & 4)
        # 3a. Decomposition
        decomp_prompt = f"Decompose this {q_class} query into sub-questions. Output JSON list."
        json.loads("".join(list(self.engine.generate(query, decomp_prompt))))

        # 4. Multi-Candidate Generation (LAYER 4)
        # Generate K=3 candidates
        candidates = []
        for _ in range(3):
            cand = "".join(list(self.engine.generate(query, "Provide a structured answer: [Goal][Approach][Answer]")))
            candidates.append(cand)

        # 5. Scoring & Uncertainty (LAYER 5, 6, 7)
        rubric_weights = self.rubric.generate_rubric(q_class.lower())
        scores = self.scorer.score_candidates(candidates, rubric_weights, self.engine)
        conf_status, variance = self.scorer.evaluate_uncertainty(scores)

        # 6. Selection
        if conf_status == "LOW_CONFIDENCE":
            return {
                "status": "UNCERTAINTY",
                "message": "Low confidence detected due to high score variance.",
                "options": candidates # Return multiple perspectives
            }
        
        best_idx = scores.index(max(scores))
        return {
            "status": "SUCCESS",
            "mode": "MEASURABLE",
            "result": candidates[best_idx],
            "confidence": max(scores)
        }
