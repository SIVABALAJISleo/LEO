"""
backend/intent/classifier.py
Tier 1: Intent Classification & Semantic Normalization Engine
"""
import math
import re
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class IntentClassifier:
    """
    Highly optimized CPU-native intent classifier.
    Performs semantic normalization, Shannon entropy scoring, ambiguity detection,
    and maps queries to optimal execution paths.
    """
    
    WORKLOAD_CLASSES = {
        "deterministic": "deterministic workflow",
        "retrieval": "retrieval lookup",
        "symbolic": "symbolic reasoning",
        "local": "local inference",
        "cloud": "cloud fallback",
        "multimodal": "multimodal request",
        "agent": "agent execution",
        "code": "code generation",
        "policy": "policy reasoning"
    }

    def __init__(self):
        self.status = "ACTIVE"
        # Compile patterns for fast CPU-native regex matching
        self.patterns = {
            "policy": re.compile(r"\b(policy|compliance|rule|hr|regulation|contract|legal|clause|accord|agreement)\b", re.I),
            "symbolic": re.compile(r"\b(calculate|solve|integral|derivative|equation|schedule|constraint|optimize|math)\b", re.I),
            "code": re.compile(r"\b(python|javascript|def |function|class |code|script|compile|syntax)\b", re.I),
            "retrieval": re.compile(r"\b(search|find|lookup|fetch|get|document|database|file|history|provenance)\b", re.I),
            "multimodal": re.compile(r"\b(image|screenshot|chart|invoice|diagram|pdf|ocr|visual|scan|photo)\b", re.I),
            "agent": "agent execution"
        }

    def normalize_query(self, query: str) -> str:
        """Applies basic semantic cleaning and normalization."""
        # Convert to lowercase and remove extraneous whitespaces/symbols
        normalized = query.lower().strip()
        normalized = re.sub(r"[^\w\s\-\/\.]", "", normalized)
        return normalized

    def calculate_entropy(self, text: str) -> float:
        """Computes Shannon Entropy of the character distribution to gauge complexity."""
        if not text:
            return 0.0
        entropy = 0.0
        length = len(text)
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1
        for count in freq.values():
            p = count / length
            entropy -= p * math.log2(p)
        return round(entropy, 4)

    def classify(self, query: str) -> Dict[str, Any]:
        """
        Classifies incoming query, estimates confidence, detects ambiguity,
        and assigns workload categorization.
        """
        normalized = self.normalize_query(query)
        entropy = self.calculate_entropy(normalized)
        
        # Default fallback
        workload = self.WORKLOAD_CLASSES["local"]
        confidence = 0.80
        ambiguity_detected = False
        
        # Ambiguity detection heuristics
        if len(normalized) < 5:
            ambiguity_detected = True
            confidence = 0.40
        elif entropy > 5.5:
            # Extremely high entropy may suggest random input / garbage payload
            ambiguity_detected = True
            confidence = 0.50

        # Run rule-based classification cascade
        if self.patterns["policy"].search(normalized):
            workload = self.WORKLOAD_CLASSES["policy"]
            confidence = 0.95
        elif self.patterns["symbolic"].search(normalized):
            workload = self.WORKLOAD_CLASSES["symbolic"]
            confidence = 0.98
        elif self.patterns["code"].search(normalized):
            workload = self.WORKLOAD_CLASSES["code"]
            confidence = 0.92
        elif self.patterns["multimodal"].search(normalized):
            workload = self.WORKLOAD_CLASSES["multimodal"]
            confidence = 0.90
        elif self.patterns["retrieval"].search(normalized):
            workload = self.WORKLOAD_CLASSES["retrieval"]
            confidence = 0.94
            
        # If query contains explicit instruction override signals, mark for agent execution
        if any(sig in normalized for sig in ["override", "escalate", "agent", "route to"]):
            workload = self.WORKLOAD_CLASSES["agent"]
            confidence = 0.95

        return {
            "query": query,
            "normalized_query": normalized,
            "entropy": entropy,
            "workload_class": workload,
            "confidence": confidence,
            "ambiguity_detected": ambiguity_detected
        }

# Global singleton classifier
global_intent_classifier = IntentClassifier()
