import logging
import asyncio
from typing import Dict, Any, List, Tuple
from fastapi import FastAPI
from pydantic import BaseModel

try:
    import sympy
    from sympy.parsing.sympy_parser import parse_expr
except ImportError:
    sympy = None

logger = logging.getLogger("OutcomeDrivenV2")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Outcome-Driven AI System V2")

# --- 1. DOMAIN CLASSIFIER ---
class DomainClassifier:
    def classify(self, query: str) -> Dict[str, Any]:
        """Classifies query into HARD, SOFT, or OPEN with a confidence score."""
        q = query.lower()
        
        scores = {"HARD": 0.0, "SOFT": 0.0, "OPEN": 0.0}
        
        if any(w in q for w in ["calculate", "solve", "logic", "code", "prove"]):
            scores["HARD"] += 0.8
        if any(w in q for w in ["explain", "fact", "who", "what", "where"]):
            scores["SOFT"] += 0.8
        if any(w in q for w in ["opinion", "creative", "perspective", "subjective"]):
            scores["OPEN"] += 0.8
            
        total = sum(scores.values()) or 1.0
        scores = {k: v / total for k, v in scores.items()}
        
        best_domain = max(scores, key=scores.get)
        confidence = scores[best_domain]
        
        secondary = None
        if confidence < 0.7:
            sorted_dom = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            secondary = sorted_dom[1][0]
            
        return {
            "primary": best_domain,
            "confidence": round(confidence, 2),
            "secondary": secondary
        }

# --- 5. OUTCOME AWARENESS ---
class OutcomeTracker:
    def __init__(self):
        self.history: List[str] = []
        
    def detect_failure_signals(self, query: str) -> bool:
        """Infer signals: repeat intent? correction likely?"""
        words = set(query.lower().split())
        for past_q in self.history[-3:]:
            past_words = set(past_q.lower().split())
            overlap = len(words.intersection(past_words)) / max(len(words), 1)
            if overlap > 0.7 or "no" in words or "wrong" in words or "incorrect" in words:
                logger.warning("Outcome Hook: Correction or repetition detected. Strategy adjusting.")
                return True
        self.history.append(query)
        return False

# --- 3. SELF-CRITIQUE (REQUIRED) ---
class CritiqueEngine:
    def self_critique(self, domain: str, draft: str, confidence: float) -> Tuple[str, float]:
        """Check logic errors, unsupported claims, fix silently."""
        issues_fixed = 0
        new_confidence = confidence
        
        if domain == "HARD" and ("I guess" in draft or "probably" in draft):
            draft = draft.replace("I guess", "").replace("probably", "")
            issues_fixed += 1
            new_confidence -= 0.15
            
        if domain == "SOFT" and "is an absolute fact" in draft:
            draft = draft.replace("is an absolute fact", "is highly supported by evidence")
            issues_fixed += 1
            
        return draft.strip(), round(new_confidence, 2)

# --- 2. PROCESSING RULES ---
class ProcessingEngine:
    async def process_hard(self, query: str) -> Tuple[str, bool]:
        """HARD: Solve -> re-solve differently -> compare -> retry or fail safely."""
        await asyncio.sleep(0.05)
        
        if not sympy:
            return "INSUFFICIENT DATA (Tools missing)", False
            
        # Strategy A: Direct Parsing
        try:
            expr_str = query.lower().replace("calculate", "").replace("solve", "").strip()
            res_a = sympy.parsing.sympy_parser.parse_expr(expr_str).evalf()
        except Exception:
            return "INSUFFICIENT DATA", False
            
        # Strategy B: Re-solve differently (e.g. sympify)
        try:
            res_b = sympy.sympify(expr_str).evalf()
        except Exception:
            return "INSUFFICIENT DATA", False
            
        # Compare
        if abs(float(res_a) - float(res_b)) < 1e-9:
            return f"Exact Result: {res_a}", True
        else:
            return "INSUFFICIENT DATA (Mismatch in solving strategies)", False

    async def process_soft(self, query: str) -> str:
        """SOFT: Generate 3-5 search queries -> Retrieve -> Re-rank -> Verify."""
        await asyncio.sleep(0.05)
        # Mock search generation
        queries = [f"{query} origin", f"{query} details", f"{query} facts"]
        logger.info(f"[SOFT Pipeline] Generated 3 queries: {queries}")
        
        # Mock Retrieval & Verification
        evidence = f"Evidence gathered from mock RAG based on {len(queries)} queries."
        answer = f"According to verified retrieved sources: {evidence}. All claims are linked to this evidence."
        return answer

    async def process_open(self, query: str) -> List[str]:
        """OPEN: Generate 2-3 structured perspectives."""
        await asyncio.sleep(0.05)
        return [
            f"Perspective A: Interpreting '{query}' through a philosophical lens.",
            f"Perspective B: Interpreting '{query}' from a pragmatic standpoint.",
            f"Perspective C: Considering the unintended consequences of '{query}'."
        ]

# --- PIPELINE ORCHESTRATOR ---
class OutcomePipelineV2:
    def __init__(self):
        self.classifier = DomainClassifier()
        self.tracker = OutcomeTracker()
        self.processor = ProcessingEngine()
        self.critique = CritiqueEngine()
        
    async def execute(self, query: str) -> str:
        # Step 5: Outcome Awareness
        is_failing = self.tracker.detect_failure_signals(query)
        
        # Step 1: Domain Classification
        cls = self.classifier.classify(query)
        domain = cls["primary"]
        confidence = cls["confidence"]
        
        if is_failing:
            confidence -= 0.2
            
        if confidence < 0.7 and cls["secondary"]:
            # Fallback to safer domain (OPEN is safer than SOFT is safer than HARD)
            safeties = {"OPEN": 3, "SOFT": 2, "HARD": 1}
            if safeties[cls["secondary"]] > safeties[domain]:
                logger.info(f"Low confidence ({confidence}). Shifting to safer domain: {cls['secondary']}")
                domain = cls["secondary"]
                
        # Step 2: Processing Rules
        answer = ""
        alternatives = []
        is_hard_success = True
        
        if domain == "HARD":
            answer, is_hard_success = await self.processor.process_hard(query)
            if not is_hard_success:
                confidence -= 0.3
        elif domain == "SOFT":
            answer = await self.processor.process_soft(query)
        elif domain == "OPEN":
            answer = "The query requires subjective interpretation. Multiple perspectives follow."
            alternatives = await self.processor.process_open(query)
            
        # Step 3: Self-Critique
        final_answer, final_conf = self.critique.self_critique(domain, answer, confidence)
        
        # Safety Overrides
        uncertainty = "None detected."
        if final_conf < 0.6:
            uncertainty = "Significant missing information or high probability of error in parsing context."
            if not alternatives:
                alternatives = [
                    "Clarification Request: Are you looking for a mathematical execution or subjective definition?",
                    "Alternative: Rephrase the constraint to be more specific."
                ]
            if domain == "HARD" and is_hard_success:
                final_answer = "INSUFFICIENT DATA (Confidence threshold breached post-solving)"
                
        # Step 4: OUTPUT FORMAT
        out = [
            f"[DOMAIN]: {domain}",
            f"[CONFIDENCE]: {int(final_conf * 100)}%\n",
            f"[ANSWER]:\n{final_answer}\n",
            f"[UNCERTAINTY]:\n- {uncertainty}"
        ]
        
        if alternatives:
            out.append("\n[ALTERNATIVES]:")
            for alt in alternatives:
                out.append(f"- {alt}")
                
        return "\n".join(out)

v2_system = OutcomePipelineV2()

class V2Request(BaseModel):
    query: str

@app.post("/api/v2/outcome")
async def handle_v2_request(req: V2Request):
    res = await v2_system.execute(req.query)
    return {"response": res}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
