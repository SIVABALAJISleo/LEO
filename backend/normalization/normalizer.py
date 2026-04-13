"""
Query Normalization Engine
Extracts intent, entity, and complexity from raw user queries.
No external model dependency — pure rule-based for maximum speed.
"""
import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

STOPWORDS = {"what", "is", "the", "a", "an", "for", "to", "in", "on", "at", "by", "with", "from", "and", "or", "of", "about"}

INTENT_PATTERNS = {
    "definition":   [r"what is", r"define", r"meaning", r"explain"],
    "comparison":   [r"vs", r"versus", r"compare", r"difference"],
    "how_to":       [r"how to", r"how do", r"how can", r"how does"],
    "calculation":  [r"calculate", r"compute", r"solve"],
    "list":         [r"list", r"give me", r"examples", r"name"],
}

SYNONYMS = {
    "llm": ["large language model", "gpt", "model", "transformer"],
    "ai": ["artificial intelligence", "intelligent system", "machine learning", "ml"],
    "fix": ["repair", "solve", "remedy", "debug", "correct"],
    "benefits": ["advantages", "pros", "positives", "good features"],
}

def lemmatize(word: str) -> str:
    """Simple heuristic lemmatization for ultra-normalization."""
    if word.endswith("ies") and len(word) > 4: return word[:-3] + "y"
    if word.endswith("es") and len(word) > 3: return word[:-2]
    if word.endswith("s") and len(word) > 3 and not word.endswith("ss"): return word[:-1]
    if word.endswith("ing") and len(word) > 5: return word[:-3]
    if word.endswith("ed") and len(word) > 4: return word[:-2]
    return word

class QueryNormalizer:
    """
    ULTRA NORMALIZATION ENGINE (Point 1).
    Collapses similar queries into unique canonical signatures.
    """
    def normalize(self, query: str) -> Dict[str, Any]:
        raw_q = query.lower().strip()
        
        # 1. Stopword Removal & Ultra-Cleansing
        words = [lemmatize(w) for w in re.findall(r'\w+', raw_q) if w not in STOPWORDS]
        clean_q = " ".join(words)
        
        # 2. Intent Parsing
        intent = self._extract_intent(raw_q)
        entity = self._extract_entity(clean_q)
        
        # 3. Family ID Mapping (Point 2)
        family_id = self.get_family_id(clean_q, intent, entity)
        
        return {
            "raw": query,
            "clean": clean_q,
            "intent": intent,
            "entity": entity,
            "family_id": family_id,
            "canonical": family_id # Map canonical to family_id for system-wide collapse
        }

    def get_family_id(self, query: str, intent: str, entity: str) -> str:
        """Point 2: Map all variations to a single family_id."""
        if intent != "general" and entity != "GENERAL":
            return f"fam:{intent}:{entity}".lower()
        return query.lower().strip().replace(" ", "_")

    def get_canonical_form(self, query: str, intent: str, entity: str) -> str:
        return self.get_family_id(query, intent, entity)

    def _extract_intent(self, q: str) -> str:
        for intent, patterns in INTENT_PATTERNS.items():
            if any(p in q for p in patterns):
                return intent
        return "general"

    def _extract_entity(self, q: str) -> str:
        # Lemmatized synonym mapping
        for canonical, variants in SYNONYMS.items():
            if any(v in q for v in variants + [canonical]):
                return canonical.upper()
        
        words = [w for w in q.split() if len(w) > 3]
        return words[0].upper() if words else "GENERAL"

global_normalizer = QueryNormalizer()
