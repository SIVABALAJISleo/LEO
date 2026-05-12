import re
import logging
from typing import Dict, Any, List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import skfuzzy as fuzzy
from skfuzzy import control as ctrl

logger = logging.getLogger(__name__)

class IntentEngine:
    """
    Module 1: INPUT -> INTENT ENGINE
    Uses sentence-transformers for embeddings and fuzzy logic for confidence tolerance.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        # Predefined canonical intents for comparison
        self.canonical_intents = {
            "information": "Request for general information or knowledge",
            "action": "Request to perform a specific action or command",
            "clarification": "Request for more details or explaining a concept",
            "troubleshoot": "Request to fix a problem or error",
            "greeting": "General greeting or polite interaction",
            "navigation": "Request to go to a specific page or section"
        }
        self.intent_labels = list(self.canonical_intents.keys())
        self.intent_embeddings = self.model.encode(list(self.canonical_intents.values()))
        
        # Setup Fuzzy Logic for Confidence
        self.setup_fuzzy()

    def setup_fuzzy(self):
        """Initializes fuzzy inference system for confidence scoring."""
        # Antecedents (inputs)
        similarity = ctrl.Antecedent(np.arange(0, 1.1, 0.1), 'similarity')
        clarity = ctrl.Antecedent(np.arange(0, 1.1, 0.1), 'clarity')
        
        # Consequent (output)
        confidence = ctrl.Consequent(np.arange(0, 1.1, 0.1), 'confidence')
        
        # Membership functions
        similarity['low'] = fuzzy.trimf(similarity.universe, [0, 0, 0.5])
        similarity['medium'] = fuzzy.trimf(similarity.universe, [0.3, 0.5, 0.8])
        similarity['high'] = fuzzy.trimf(similarity.universe, [0.6, 1.0, 1.0])
        
        clarity['poor'] = fuzzy.trimf(clarity.universe, [0, 0, 0.4])
        clarity['fair'] = fuzzy.trimf(clarity.universe, [0.3, 0.6, 0.8])
        clarity['good'] = fuzzy.trimf(clarity.universe, [0.7, 1.0, 1.0])
        
        confidence['low'] = fuzzy.trimf(confidence.universe, [0, 0, 0.4])
        confidence['medium'] = fuzzy.trimf(confidence.universe, [0.3, 0.6, 0.8])
        confidence['high'] = fuzzy.trimf(confidence.universe, [0.7, 1.0, 1.0])
        
        # Rules
        rule1 = ctrl.Rule(similarity['high'] & clarity['good'], confidence['high'])
        rule2 = ctrl.Rule(similarity['medium'] | clarity['fair'], confidence['medium'])
        rule3 = ctrl.Rule(similarity['low'] | clarity['poor'], confidence['low'])
        
        conf_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
        self.conf_simulator = ctrl.ControlSystemSimulation(conf_ctrl)

    def normalize(self, query: str) -> str:
        """Normalizes input (lowercase, clean, rewrite if needed)."""
        query = query.lower().strip()
        query = re.sub(r'[^\w\s\?]', '', query)
        # Simple rewrite: remove filler words
        fillers = ["please", "could", "you", "tell", "me", "what", "is"]
        # but don't remove if it makes the query empty
        return query

    def detect_intent(self, query: str) -> Dict[str, Any]:
        """Calculates intent and fuzzy confidence."""
        clean_query = self.normalize(query)
        query_embedding = self.model.encode([clean_query])[0]
        
        # Calculate similarities
        similarities = np.dot(self.intent_embeddings, query_embedding) / (
            np.linalg.norm(self.intent_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]
        intent = self.intent_labels[best_idx]
        
        # Heuristic for clarity: based on length and word count
        words = clean_query.split()
        clarity_score = min(1.0, len(words) / 15.0) if words else 0.0
        
        # Fuzzy Confidence
        try:
            self.conf_simulator.input['similarity'] = float(best_similarity)
            self.conf_simulator.input['clarity'] = float(clarity_score)
            self.conf_simulator.compute()
            fuzzy_conf = self.conf_simulator.output['confidence']
        except Exception:
            fuzzy_conf = best_similarity * 0.8 + clarity_score * 0.2
            
        return {
            "query": query,
            "normalized_query": clean_query,
            "intent": intent,
            "confidence": round(float(fuzzy_conf), 4),
            "raw_similarity": round(float(best_similarity), 4)
        }

global_intent_engine = IntentEngine()
