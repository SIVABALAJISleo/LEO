import os
import json
import logging
import asyncio
import numpy as np
from typing import Dict, Any, List, Tuple
from fastapi import FastAPI
from pydantic import BaseModel

try:
    import sympy
    from sympy.parsing.sympy_parser import parse_expr
except ImportError:
    sympy = None

logger = logging.getLogger("OutcomeDrivenV3")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Outcome-Driven AI System V3")

# --- 1. DOMAIN CLASSIFICATION & 2. CONFIDENCE GATING ---
class DomainClassifier:
    def classify(self, query: str) -> Dict[str, Any]:
        """Classify input into HARD, SOFT, OPEN with confidence."""
        q = query.lower()
        scores = {"HARD": 0.0, "SOFT": 0.0, "OPEN": 0.0}
        
        # Keyword-based heuristics (Mocking an intent classifier)
        if any(w in q for w in ["calculate", "math", "code", "logic", "execute"]):
            scores["HARD"] += 0.8
        if any(w in q for w in ["fact", "explain", "history", "what", "where"]):
            scores["SOFT"] += 0.8
        if any(w in q for w in ["opinion", "creative", "perspective", "idea"]):
            scores["OPEN"] += 0.8
            
        total = sum(scores.values()) or 1.0
        scores = {k: v / total for k, v in scores.items()}
        
        primary_domain = max(scores, key=scores.get)
        confidence = scores[primary_domain]
        
        # Gating logic
        secondary = None
        if confidence < 0.7:
            sorted_dom = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            secondary = sorted_dom[1][0]
            
        return {
            "primary": primary_domain,
            "secondary": secondary,
            "confidence": round(confidence, 2)
        }

# --- 5. OUTCOME AWARENESS ---
class OutcomeAwareness:
    def __init__(self):
        self.user_history: List[str] = []
        
    def detect_failure_signals(self, query: str) -> float:
        """Infer repeat intent or task failure. Returns confidence penalty."""
        words = set(query.lower().split())
        penalty = 0.0
        
        if any(w in words for w in ["wrong", "no", "incorrect", "fail"]):
            logger.warning("[OUTCOME] Correction likely detected.")
            penalty += 0.2
            
        for past_q in self.history[-3:] if hasattr(self, "history") else []:
            past_words = set(past_q.lower().split())
            overlap = len(words.intersection(past_words)) / max(len(words), 1)
            if overlap > 0.7:
                logger.warning("[OUTCOME] Repeat intent detected. Failure suspected.")
                penalty += 0.15
                
        self.user_history.append(query)
        return penalty

# --- 3. DOMAIN-SPECIFIC PROCESSING RULES ---
class ProcessingEngine:
    async def process_hard(self, query: str) -> Tuple[str, bool]:
        """HARD: Solve -> execute -> re-solve differently -> compare -> retry or fail safely."""
        await asyncio.sleep(0.05)
        
        if not sympy:
            return "INSUFFICIENT DATA (Tooling unavailable)", False
            
        try:
            expr_str = query.lower().replace("calculate", "").replace("solve", "").strip()
            # Strategy 1: Direct evalf
            res_1 = sympy.parsing.sympy_parser.parse_expr(expr_str).evalf()
            # Strategy 2: Sympify
            res_2 = sympy.sympify(expr_str).evalf()
            
            if abs(float(res_1) - float(res_2)) < 1e-9:
                return f"Exact Verified Result: {res_1}", True
            else:
                return "INSUFFICIENT DATA (Mismatch in execution verification)", False
        except Exception:
            return "INSUFFICIENT DATA (Not mathematically provable)", False

    async def process_soft(self, query: str) -> Tuple[str, bool]:
        """SOFT: Generate queries -> Retrieve -> Re-rank -> Verify."""
        await asyncio.sleep(0.05)
        
        # Step 1: Generate 3-5 variations
        variations = [f"{query} overview", f"{query} data", f"{query} evidence"]
        logger.info(f"[SOFT] Generated queries: {variations}")
        
        # Step 2: Retrieve (Semantic + Keyword) Mock
        raw_evidence = [f"Doc A (Keyword Match): Details on {query}", f"Doc B (Semantic Match): Conceptual facts."]
        
        # Step 3: Re-rank & Verify Mock
        best_evidence = raw_evidence[1] # Pretend semantic match won
        
        answer = f"According to retrieved evidence '{best_evidence}', the claim holds."
        return answer, True

    async def process_open(self, query: str) -> List[str]:
        """OPEN: Generate 2-3 structured perspectives."""
        await asyncio.sleep(0.05)
        return [
            f"Perspective A: Interpreting '{query}' via structural analysis.",
            f"Perspective B: Viewing '{query}' through a human-centric lens."
        ]

# --- 4. SELF-CRITIQUE & VERIFICATION ---
class CritiqueVerification:
    def verify(self, domain: str, draft: str, confidence: float) -> Tuple[str, float]:
        """Check logic errors, fix silently. Optional: 2 candidates."""
        new_conf = confidence
        
        if domain == "HARD" and "might be" in draft:
            draft = draft.replace("might be", "is exactly")
            new_conf -= 0.1
            
        if domain == "SOFT" and "is absolutely" in draft:
            draft = draft.replace("is absolutely", "is heavily supported by evidence to be")
            
        return draft.strip(), round(new_conf, 2)

# --- CORE ORCHESTRATOR ---
class OutcomeSystemV3:
    def __init__(self):
        self.classifier = DomainClassifier()
        self.awareness = OutcomeAwareness()
        self.processor = ProcessingEngine()
        self.critique = CritiqueVerification()
        
    async def execute(self, query: str) -> str:
        # 1. Outcome Awareness Hook
        penalty = self.awareness.detect_failure_signals(query)
        
        # 2. Domain Classification & Confidence Check
        cls = self.classifier.classify(query)
        domain = cls["primary"]
        confidence = cls["confidence"] - penalty
        
        if confidence < 0.7 and cls["secondary"]:
            # Run top 2 domains, choose safer output
            safeties = {"OPEN": 3, "SOFT": 2, "HARD": 1}
            if safeties[cls["secondary"]] > safeties[domain]:
                logger.info(f"Low confidence ({confidence}). Shifting to safer domain: {cls['secondary']}")
                domain = cls["secondary"]
                
        # 3. Domain-Specific Processing
        answer = ""
        alternatives = []
        is_hard_success = True
        
        if domain == "HARD":
            answer, is_hard_success = await self.processor.process_hard(query)
            if not is_hard_success:
                confidence -= 0.4
        elif domain == "SOFT":
            answer, is_soft_supported = await self.processor.process_soft(query)
            if not is_soft_supported:
                confidence -= 0.3
        elif domain == "OPEN":
            answer = "Open-ended inquiry mapped. Review alternatives."
            alternatives = await self.processor.process_open(query)
            
        # 4. Self-Critique & Verification
        final_answer, final_conf = self.critique.verify(domain, answer, confidence)
        
        # Limits / Error Handling
        uncertainty = "No immediate gaps detected in retrieved context."
        if final_conf < 0.6:
            uncertainty = "High potential for context gap or missing constraints."
            if not alternatives:
                alternatives = [
                    "Alternative A: Could you clarify the logical constraints?",
                    "Alternative B: Provide additional verifiable facts to proceed."
                ]
            if domain == "HARD":
                final_answer = "INSUFFICIENT DATA"
                
        # 5. Safe Output Formulation
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

os_v3 = OutcomeSystemV3()

class CoreRequest(BaseModel):
    query: str

@app.post("/api/v3/outcome")
async def outcome_v3_endpoint(req: CoreRequest):
    res = await os_v3.execute(req.query)
    return {"response": res}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
