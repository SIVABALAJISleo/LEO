"""
Query Normalization Engine
Extracts intent, entity, and complexity from raw user queries.
No external model dependency — pure rule-based for maximum speed.
"""
import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

INTENT_PATTERNS = {
    "definition":   [r"\bwhat is\b", r"\bdefine\b", r"\bmeaning of\b", r"\bexplain\b"],
    "comparison":   [r"\bvs\b", r"\bversus\b", r"\bcompare\b", r"\bdifference between\b"],
    "how_to":       [r"\bhow (to|do|can|does)\b", r"\bsteps to\b", r"\bway to\b"],
    "calculation":  [r"\bcalculate\b", r"\bcompute\b", r"\bsolve\b", r"\d+\s*[\+\-\*\/]\s*\d+"],
    "list":         [r"\blist\b", r"\bgive me\b", r"\bexamples of\b", r"\bname\b"],
    "summary":      [r"\bsummariz\b", r"\boverview\b", r"\btldr\b", r"\bbriefly\b"],
    "explanation":  [r"\bwhy\b", r"\breason\b", r"\bcause\b", r"\bbecause\b"],
}

ENTITY_PATTERNS = [
    r"what is ([A-Za-z0-9\-]+)",
    r"explain ([A-Za-z0-9\-]+)",
    r"define ([A-Za-z0-9\-]+)",
    r"how (?:to|does) ([A-Za-z0-9\-]+)",
]

COMPLEXITY_RULES = {
    "simple":  lambda q: len(q.split()) < 8 and "?" in q,
    "complex": lambda q: len(q.split()) > 25 or any(w in q.lower() for w in ["compare", "analyze", "architecture", "design"]),
}


class QueryNormalizer:
    """Lightweight rule-based query normalization. Zero model calls."""

    def normalize(self, query: str) -> Dict[str, Any]:
        query = query.strip()
        q_lower = query.lower()

        intent = self._extract_intent(q_lower)
        entity = self._extract_entity(q_lower)
        complexity = self._estimate_complexity(q_lower)

        result = {
            "original": query,
            "intent": intent,
            "entity": entity,
            "type": "simple" if complexity == "simple" else "complex",
            "complexity": complexity,
            "word_count": len(query.split()),
        }
        logger.debug(f"query_normalized: {result}")
        return result

    def _extract_intent(self, q: str) -> str:
        for intent, patterns in INTENT_PATTERNS.items():
            for p in patterns:
                if re.search(p, q):
                    return intent
        return "general"

    def _extract_entity(self, q: str) -> str:
        for p in ENTITY_PATTERNS:
            m = re.search(p, q)
            if m:
                return m.group(1).upper()
        # Fallback: extract longest capitalized word
        words = [w for w in q.split() if w[0].isupper() and len(w) > 2]
        return words[0] if words else "general"

    def _estimate_complexity(self, q: str) -> str:
        if COMPLEXITY_RULES["simple"](q):
            return "simple"
        if COMPLEXITY_RULES["complex"](q):
            return "complex"
        return "medium"


global_normalizer = QueryNormalizer()
