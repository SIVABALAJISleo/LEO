"""
backend/intent/classifier.py
Ultra-fast, CPU-native intent classification, query entropy scoring, and ambiguity detection.
Categorizes queries into deterministic workflow, retrieval, symbolic reasoning, local inference, etc.
"""
import re
import math
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class IntentClassifier:
    """
    Analyzes queries to determine lexical entropy, structural complexity, and semantic intent.
    Helps LEO route queries to the correct layer in the execution cascade, bypassing dense inference.
    """

    # Keyword mappings to detect specific intents
    INTENT_TRIGGERS = {
        "symbolic_reasoning": re.compile(
            r"\b(policy|rules|compliance|violation|contradiction|conflict|prove|satisfy|z3|solver|constraint|schedule|hr rules|access control|allow|deny)\b", re.I
        ),
        "deterministic_workflow": re.compile(
            r"\b(onboard|offboard|ticket|status|approve|reject|escalate|workflow|trigger|step|sequence|fsm|fsm_rules)\b", re.I
        ),
        "retrieval_lookup": re.compile(
            r"\b(find|search|lookup|retrieve|document|wiki|database|reference|kb|grounded|rag|llama.?index|corpus|docx|pdf)\b", re.I
        ),
        "multimodal_request": re.compile(
            r"\b(ocr|screenshot|chart|diagram|invoice|receipt|audio|transcript|voice|image|whisper|smolvlm|yolo)\b", re.I
        ),
        "code_generation": re.compile(
            r"\b(code|python|typescript|javascript|rust|compile|syntax|refactor|debug|function|class|algorithm)\b", re.I
        ),
        "local_inference": re.compile(
            r"\b(local model|run model|quantize|gguf|phi|gemma|mistral|llama|vulkan|igpu|bitnet)\b", re.I
        )
    }

    HIGH_ENTROPY_INDICATORS = re.compile(
        r"\b(synthesize|strategy|predict|novel|creative|imagine|speculate|design|architect|evaluate|tradeoff|explain why)\b", re.I
    )

    @classmethod
    def calculate_entropy(cls, text: str) -> float:
        """Computes approximate Shannon entropy of query token distribution."""
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            return 0.0
        
        freq: Dict[str, int] = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
            
        total = len(tokens)
        ent = -sum((c / total) * math.log2(c / total) for c in freq.values())
        
        # Normalize by maximum potential entropy of the query length
        max_ent = math.log2(max(total, 2))
        return min(ent / max_ent, 1.0)

    @classmethod
    def detect_ambiguity(cls, text: str) -> Tuple[bool, float]:
        """Detects if query is ambiguous (vague, too short, lacking nouns)."""
        tokens = re.findall(r"\w+", text.strip())
        if len(tokens) <= 3:
            return True, 0.85  # Highly ambiguous if very short
            
        # Check for vague index words
        vague_patterns = re.compile(r"\b(stuff|thing|do something|help me|run|fix)\b", re.I)
        matches = len(vague_patterns.findall(text))
        if matches > 1:
            return True, min(0.4 + (matches * 0.2), 0.95)
            
        return False, 0.10

    @classmethod
    def classify(cls, text: str) -> Dict[str, Any]:
        """
        Classifies the query and generates structural metadata.
        Returns workload categorization, confidence, entropy, and ambiguity indicators.
        """
        entropy = cls.calculate_entropy(text)
        is_ambiguous, ambiguity_score = cls.detect_ambiguity(text)
        
        # Normalization: lowercased, clean spacing
        normalized_query = re.sub(r"\s+", " ", text.lower().strip())
        
        # Categorize intent
        workload_class = "local_inference"  # Default fallback path
        confidence = 0.75

        # Scan for triggers
        matched_triggers = []
        for w_class, pattern in cls.INTENT_TRIGGERS.items():
            if pattern.search(normalized_query):
                matched_triggers.append(w_class)

        if matched_triggers:
            # Select highest priority trigger
            # Priority: symbolic > deterministic > retrieval > multimodal > code
            priority = ["symbolic_reasoning", "deterministic_workflow", "retrieval_lookup", "multimodal_request", "code_generation", "local_inference"]
            for p in priority:
                if p in matched_triggers:
                    workload_class = p
                    confidence = 0.95
                    break
        elif cls.HIGH_ENTROPY_INDICATORS.search(normalized_query) or entropy > 0.82:
            workload_class = "cloud_fallback"
            confidence = 0.85
        elif entropy < 0.35:
            workload_class = "deterministic_workflow"
            confidence = 0.90

        return {
            "query": text,
            "normalized_query": normalized_query,
            "workload_class": workload_class,
            "confidence": confidence,
            "entropy_score": round(entropy, 4),
            "is_ambiguous": is_ambiguous,
            "ambiguity_score": round(ambiguity_score, 4)
        }
