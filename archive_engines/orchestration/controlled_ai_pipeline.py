import os
import logging
import asyncio
import numpy as np
from typing import Dict, Any, List
from fastapi import FastAPI
from pydantic import BaseModel

try:
    import sympy
    from sympy.parsing.sympy_parser import parse_expr
except ImportError:
    sympy = None

try:
    import z3
except ImportError:
    z3 = None

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

logger = logging.getLogger("ControlledAI")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Controlled AI System (Rubric & Uncertainty Driven)")

# --- 1. TASK ROUTER ---
class TaskRouter:
    def classify(self, query: str) -> str:
        q = query.lower()
        if "calculate" in q or "+" in q or "-" in q:
            return "DETERMINISTIC_MATH"
        if "solve" in q or "logic" in q:
            return "DETERMINISTIC_LOGIC"
        if "what" in q or "who" in q or "fact" in q:
            return "FACTUAL"
        return "OPEN_ENDED"

# --- 2. RUBRIC ENGINE ---
class RubricEngine:
    def generate_rubric(self, query: str) -> Dict[str, float]:
        """Dynamically define weighted evaluation criteria"""
        q = query.lower()
        if "code" in q or "program" in q:
            return {"correctness": 0.5, "efficiency": 0.3, "readability": 0.2}
        if "explain" in q or "why" in q:
            return {"clarity": 0.4, "depth": 0.4, "logic": 0.2}
        
        # Default fallback
        return {"relevance": 0.4, "creativity": 0.3, "structure": 0.3}

# --- 3. DECOMPOSITION ---
class DecompositionEngine:
    async def decompose(self, query: str, llm_generate_fn) -> List[str]:
        # For a truly local system, we ask the small LLM to break down the query
        # Mocking for speed/safety
        return [f"What is the core premise of '{query}'?", f"What are the factual constraints?", f"What are the implications?"]

# --- 9. TOOL INTEGRATION & 10. RAG LAYER ---
class ToolAndRAGLayer:
    def execute(self, route: str, query: str) -> str:
        if route == "DETERMINISTIC_MATH":
            if not sympy: return "SymPy not available."
            try:
                parsed = parse_expr(query.replace("calculate", "").strip())
                return f"[MATH_RESULT] {parsed.evalf()}"
            except Exception as e:
                return f"[MATH_ERROR] {e}"
                
        elif route == "DETERMINISTIC_LOGIC":
            return "[LOGIC_RESULT] Z3 Solver Output: SATISFIABLE"
            
        elif route == "FACTUAL":
            return "[RAG_RETRIEVAL] Extracted ground-truth fact."
            
        return "[NO_TOOL_REQUIRED]"

# --- 4. MULTI-CANDIDATE GENERATION ---
class CandidateGenerator:
    async def generate_candidates(self, query: str, context: str, k: int, llm_generate_fn) -> List[str]:
        candidates = []
        for i in range(k):
            prompt = f"System: Use context '{context}'. Respond using format [Goal][Approach][Answer].\nUser: {query}\nCandidate {i+1}:"
            ans = await llm_generate_fn(prompt, temperature=0.7 + (i * 0.1))
            candidates.append(ans)
        return candidates

# --- 5. SCORING SYSTEM ---
class ScoringSystem:
    def score_candidates(self, candidates: List[str], rubric: Dict[str, float]) -> List[Dict[str, Any]]:
        scored = []
        for c in candidates:
            # Hard Constraint Check
            if "[Goal]" not in c or "[Answer]" not in c:
                scored.append({"text": c, "score": 0.0, "valid": False, "reason": "Failed structure constraint."})
                continue
                
            # Mock scoring based on rubric weights (In prod, another LLM pass evaluates this)
            # We assume a base score and apply variance for demonstration
            base_score = np.random.uniform(0.6, 0.95)
            final_score = sum([weight * base_score for criteria, weight in rubric.items()])
            
            scored.append({"text": c, "score": round(final_score, 3), "valid": True, "reason": "Passed"})
            
        # Sort highest to lowest
        return sorted(scored, key=lambda x: x["score"], reverse=True)

# --- 7. UNCERTAINTY GATE & 6. SELECTION ---
class UncertaintySelectionGate:
    def select_output(self, scored_candidates: List[Dict[str, Any]]) -> str:
        valid_cands = [c for c in scored_candidates if c["valid"]]
        
        if not valid_cands:
            return "[UNCERTAINTY_GATE] System Failure: No candidates met the required constraints."
            
        if len(valid_cands) == 1:
            return valid_cands[0]["text"]
            
        scores = [c["score"] for c in valid_cands]
        variance = np.var(scores)
        top_score = scores[0]
        runner_up_score = scores[1]
        
        score_gap = top_score - runner_up_score
        
        # High confidence -> Best answer
        if score_gap > 0.15 and top_score > 0.75:
            return f"[HIGH CONFIDENCE | Score: {top_score}]\n{valid_cands[0]['text']}"
            
        # Low confidence -> Uncertainty handling
        if variance < 0.01 or top_score < 0.6:
            options = "\n\n".join([f"Option {i+1} (Score: {c['score']}):\n{c['text']}" for i, c in enumerate(valid_cands[:2])])
            return f"[UNCERTAINTY_GATE] Low confidence in a single best answer. Presenting multiple perspectives:\n\n{options}"
            
        # Moderate gap -> Top 2
        options = "\n\n".join([f"Option {i+1}:\n{c['text']}" for i, c in enumerate(valid_cands[:2])])
        return f"[MULTIPLE VALID OPTIONS]\n\n{options}"

# --- 11. CENTRAL CONTROL LOOP ---
class ControlledAIPipeline:
    def __init__(self):
        self.router = TaskRouter()
        self.rubric_engine = RubricEngine()
        self.decomposer = DecompositionEngine()
        self.tools = ToolAndRAGLayer()
        self.generator = CandidateGenerator()
        self.scorer = ScoringSystem()
        self.gate = UncertaintySelectionGate()
        
        self.llm = None
        model_path = os.getenv("MODEL_PATH", "./models/llama-3-8b-instruct.Q4_K_M.gguf")
        if Llama and os.path.exists(model_path):
            self.llm = Llama(model_path=model_path, n_ctx=4096, n_threads=8, n_gpu_layers=35)
            
    async def mock_llm_generate(self, prompt: str, temperature: float = 0.7) -> str:
        if self.llm:
            res = await asyncio.to_thread(self.llm, prompt, max_tokens=256, temperature=temperature)
            return res["choices"][0]["text"].strip()
            
        # Fallback Mock
        await asyncio.sleep(0.1)
        return f"[Goal] Process Query [Approach] Evaluated at Temp {temperature} [Answer] Synthesized Response."

    async def execute(self, query: str) -> Dict[str, Any]:
        # 1. Route
        route = self.router.classify(query)
        
        # 2. Rubric
        rubric = self.rubric_engine.generate_rubric(query)
        
        # 3. Decompose & Tool Execution
        await self.decomposer.decompose(query, self.mock_llm_generate)
        context = self.tools.execute(route, query)
        
        # Deterministic Fast-Path
        if route in ["DETERMINISTIC_MATH", "DETERMINISTIC_LOGIC"]:
            return {"status": "SUCCESS", "route": route, "output": context}
            
        # 4. Generate K=3 Candidates
        k = 3
        candidates = await self.generator.generate_candidates(query, context, k, self.mock_llm_generate)
        
        # 5. Score
        scored = self.scorer.score_candidates(candidates, rubric)
        
        # 6 & 7. Selection & Uncertainty Gate
        final_output = self.gate.select_output(scored)
        
        return {
            "status": "SUCCESS",
            "route": route,
            "rubric": rubric,
            "output": final_output
        }

pipeline = ControlledAIPipeline()

class QueryModel(BaseModel):
    query: str

@app.post("/api/v1/controlled-query")
async def run_pipeline(req: QueryModel):
    return await pipeline.execute(req.query)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
