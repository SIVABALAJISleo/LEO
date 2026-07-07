import asyncio
import logging
from typing import Dict, Any, List, Tuple
from fastapi import FastAPI
from pydantic import BaseModel

logger = logging.getLogger("OutcomeDrivenAI")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Outcome-Driven AI System")

# --- 1. DOMAIN CLASSIFIER ---
class DomainClassifier:
    def classify(self, query: str) -> Dict[str, Any]:
        """Classifies query into HARD, SOFT, or OPEN with a confidence score."""
        q = query.lower()
        
        # Heuristic scoring (MOCK of actual ML intent classification)
        scores = {"HARD": 0.0, "SOFT": 0.0, "OPEN": 0.0}
        
        if any(w in q for w in ["calculate", "solve", "code", "exact", "math"]):
            scores["HARD"] += 0.8
        if any(w in q for w in ["explain", "summarize", "history", "what is"]):
            scores["SOFT"] += 0.7
        if any(w in q for w in ["opinion", "creative", "idea", "best way"]):
            scores["OPEN"] += 0.8
            
        # Normalize
        total = sum(scores.values()) or 1.0
        scores = {k: v / total for k, v in scores.items()}
        
        best_domain = max(scores, key=scores.get)
        confidence = scores[best_domain]
        
        # If confidence < 0.7, run both likely domains
        secondary_domain = None
        if confidence < 0.7:
            sorted_domains = sorted(scores.items(), key=lambda item: item[1], reverse=True)
            secondary_domain = sorted_domains[1][0]
            
        return {
            "primary": best_domain,
            "confidence": round(confidence, 2),
            "secondary": secondary_domain,
            "all_scores": scores
        }

# --- 5. OUTCOME SIGNAL HOOKS ---
class OutcomeTracker:
    def __init__(self):
        self.history: List[str] = []
        
    def detect_failure_signals(self, query: str) -> bool:
        """
        Infer signals: Is user repeating intent? Is question refinement happening?
        Returns True if a failure or frustration is suspected.
        """
        # Simple similarity check
        words = set(query.lower().split())
        for past_q in self.history[-3:]:  # Check last 3 queries
            past_words = set(past_q.lower().split())
            overlap = len(words.intersection(past_words)) / max(len(words), 1)
            
            if overlap > 0.7:
                logger.warning(f"Outcome Hook Triggered: User repeating intent > 70% overlap. Adjusting strategy.")
                return True
                
        self.history.append(query)
        return False

# --- 3. SELF-CRITIQUE LOOP ---
class CritiqueEngine:
    def self_critique(self, domain: str, draft: str, confidence: float) -> Tuple[str, float]:
        """
        1. Check logical errors
        2. Check unsupported claims
        3. Check domain rule violations
        """
        issues_fixed = 0
        new_confidence = confidence
        
        # Strict Rule Violations
        if domain == "HARD" and "I think" in draft:
            draft = draft.replace("I think", "")
            issues_fixed += 1
            new_confidence -= 0.1 # Penalty for having to fix guessing
            
        if domain == "SOFT" and ("definitely" in draft or "100%" in draft):
            draft = draft.replace("definitely", "likely").replace("100%", "highly probable")
            issues_fixed += 1
            
        # If confidence drops below 0.6 due to issues, trigger clarification
        return draft.strip(), round(new_confidence, 2)

# --- CENTRAL PIPELINE ---
class OutcomeDrivenSystem:
    def __init__(self):
        self.classifier = DomainClassifier()
        self.tracker = OutcomeTracker()
        self.critique = CritiqueEngine()
        
    async def process_domain(self, domain: str, query: str) -> Tuple[str, List[str]]:
        """Applies Processing Rules based on Domain."""
        await asyncio.sleep(0.1) # Mock execution time
        
        alternatives = []
        if domain == "HARD":
            # STRICT execution - if fails -> INSUFFICIENT DATA
            if "fail" in query.lower():
                answer = "INSUFFICIENT DATA"
            else:
                answer = f"Exact execution result for '{query}'"
                
        elif domain == "SOFT":
            answer = f"Evidence suggests that '{query}' relates to X. Interpretation relies on Y."
            
        else: # OPEN
            answer = f"Subjective exploration of '{query}'."
            alternatives = [
                f"Option A (Perspective 1): Focus heavily on X.",
                f"Option B (Perspective 2): Prioritize Y instead."
            ]
            
        return answer, alternatives

    async def execute(self, query: str) -> str:
        # Step 5 (Early hook): Check failure signals
        is_failing = self.tracker.detect_failure_signals(query)
        
        # Step 1: Domain Classification & Step 2: Confidence Check
        classification = self.classifier.classify(query)
        domain = classification["primary"]
        confidence = classification["confidence"]
        
        if is_failing:
            confidence -= 0.2  # Drop confidence if user is repeating queries
            
        # Strategy selection
        if confidence < 0.7 and classification["secondary"]:
            logger.info(f"Low confidence ({confidence}). Running dual-domain processing: {domain} & {classification['secondary']}")
            # We choose the safer (lower risk) domain as primary in low confidence. HARD is highest risk, OPEN is lowest risk.
            risk_order = {"OPEN": 0, "SOFT": 1, "HARD": 2}
            if risk_order[classification["secondary"]] < risk_order[domain]:
                domain = classification["secondary"]
                
        # Step 3: Processing Rules
        draft_answer, alternatives = await self.process_domain(domain, query)
        
        # Step 4: Self-Critique
        final_answer, final_confidence = self.critique.self_critique(domain, draft_answer, confidence)
        
        uncertainty_msg = "None detected."
        
        # Step 6: Safety Override & Low Confidence Handling
        if final_confidence < 0.6:
            uncertainty_msg = "Data may be incomplete, or the premise of the question spans conflicting domains."
            if not alternatives:
                alternatives = [
                    "Clarification 1: Did you mean X?",
                    "Clarification 2: Or are you referring to Y?"
                ]
            if domain == "HARD":
                final_answer = "INSUFFICIENT DATA"
                
        # Step 5: Format Output
        output = [
            f"[DOMAIN]: {domain}",
            f"[CONFIDENCE]: {int(final_confidence * 100)}%",
            f"[ANSWER]:\n{final_answer}",
            f"\n[UNCERTAINTY]:\n- {uncertainty_msg}"
        ]
        
        if alternatives:
            output.append("\n[ALTERNATIVES]:")
            for alt in alternatives:
                output.append(f"- {alt}")
                
        return "\n".join(output)

# Instantiate Global System
ai_system = OutcomeDrivenSystem()

class QueryRequest(BaseModel):
    query: str

@app.post("/api/v1/outcome")
async def outcome_endpoint(req: QueryRequest):
    result = await ai_system.execute(req.query)
    return {"response": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
