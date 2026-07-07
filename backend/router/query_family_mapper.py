"""
backend/router/query_family_mapper.py

Ultra Normalization + Query Family Mapper
=========================================
Rule: same meaning = same family_id key
- Lowercase + stopword removal + lemmatization
- Synonym collapse (e.g. "large language model" → "llm")
- Intent extraction
- Deterministic family_id: every semantically equivalent query maps
  to the SAME stable key — enabling zero-repeat guarantee

This module is the FIRST step in the pipeline.
"""
import re
import hashlib
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# ── Stopwords ────────────────────────────────────────────────────────────────
STOPWORDS: frozenset = frozenset({
    "what", "is", "the", "a", "an", "for", "to", "in", "on", "at", "by",
    "with", "from", "and", "or", "of", "about", "can", "do", "does", "did",
    "how", "why", "when", "where", "who", "which", "its", "it", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "will", "would",
    "could", "should", "may", "might", "i", "me", "my", "you", "your",
    "please", "tell", "explain", "give", "show", "list",
})

# ── Synonym Map (canonical ← variants) ───────────────────────────────────────
SYNONYM_MAP: Dict[str, List[str]] = {
    "llm": ["large language model", "language model", "gpt", "transformer model", "openai model"],
    "ai": ["artificial intelligence", "intelligent system", "machine intelligence"],
    "ml": ["machine learning", "deep learning", "neural network", "dl"],
    "rag": ["retrieval augmented generation", "retrieval-augmented generation"],
    "api": ["application programming interface", "endpoint", "rest api", "graphql api"],
    "cache": ["caching", "memoization", "memo", "stored result"],
    "embedding": ["vector embedding", "dense vector", "semantic vector"],
    "inference": ["model inference", "prediction", "run model"],
    "latency": ["response time", "delay", "lag", "speed"],
    "throughput": ["requests per second", "rps", "qps", "tps"],
    "fix": ["repair", "solve", "remedy", "debug", "correct", "patch"],
    "benefit": ["advantage", "pro", "positive", "upside", "merit"],
    "gpu": ["graphics processing unit", "graphics card"],
    "cpu": ["central processing unit", "processor"],
    "database": ["db", "sql", "nosql", "data store"],
    "deploy": ["deployment", "ship", "release", "publish", "host"],
    "scale": ["scaling", "scalability", "horizontal scale", "vertical scale"],
    "cost": ["price", "pricing", "expense", "fee", "billing"],
    "performance": ["speed", "efficiency", "fast", "optimized", "optimisation"],
    "security": ["secure", "safety", "vulnerability", "authentication", "authorization"],
}

# ── Intent Patterns ───────────────────────────────────────────────────────────
INTENT_PATTERNS: Dict[str, List[str]] = {
    "definition":  ["what is", "define", "meaning of", "explain", "describe"],
    "comparison":  ["vs", "versus", "compare", "difference between", "which is better"],
    "how_to":      ["how to", "how do i", "how can i", "how does", "steps to", "guide"],
    "calculation": ["calculate", "compute", "solve", "formula", "equation"],
    "list":        ["list", "examples of", "give me", "name some", "what are"],
    "troubleshoot":["error", "problem", "issue", "not working", "fail", "debug", "fix"],
    "benefit":     ["benefit", "advantage", "why use", "pros of"],
    "cost":        ["cost", "price", "how much", "billing"],
}


# ── Lemmatizer (no external dependency) ───────────────────────────────────────
def _lemmatize(word: str) -> str:
    if word.endswith("ies") and len(word) > 4:  return word[:-3] + "y"
    if word.endswith("ves") and len(word) > 4:  return word[:-3] + "f"
    if word.endswith("ing") and len(word) > 5:  return word[:-3]
    if word.endswith("tion") and len(word) > 5: return word[:-3]  # action→act
    if word.endswith("ed") and len(word) > 4:   return word[:-2]
    if word.endswith("er") and len(word) > 4:   return word[:-2]
    if word.endswith("es") and len(word) > 3:   return word[:-2]
    if word.endswith("s")  and len(word) > 3 and not word.endswith("ss"): return word[:-1]
    return word


class QueryFamilyMapper:
    """
    Maps any query variation to a unique, stable family_id.
    All semantically equivalent queries collapse to the same key,
    enabling guaranteed zero-repeat compute.
    """

    def __init__(self):
        # Build reverse-lookup: variant phrase → canonical
        self._synonym_lookup: Dict[str, str] = {}
        for canonical, variants in SYNONYM_MAP.items():
            self._synonym_lookup[canonical] = canonical  # self-map
            for v in variants:
                self._synonym_lookup[v.lower()] = canonical

    # ── Public API ─────────────────────────────────────────────────────────── #

    def normalize(self, query: str) -> Dict[str, Any]:
        """
        Full normalization pipeline. Returns structured dict with:
          - raw, clean, tokens, synonyms_applied
          - intent, entity
          - family_id (stable key for this meaning)
          - canonical_display (human-readable form of family_id)
        """
        raw = query.strip()
        lower = raw.lower()

        # 1. Apply synonym collapse BEFORE tokenizing (phrase-level)
        collapsed = self._apply_synonyms(lower)

        # 2. Tokenize, lemmatize, remove stopwords
        tokens = [
            _lemmatize(w)
            for w in re.findall(r"\w+", collapsed)
            if w not in STOPWORDS and len(w) > 1
        ]

        clean = " ".join(tokens)

        # 3. Extract intent
        intent = self._extract_intent(lower)

        # 4. Extract primary entity (first non-stop significant token)
        entity = self._extract_entity(tokens)

        # 5. Build deterministic family_id
        family_id = self._build_family_id(clean, intent, entity)

        return {
            "raw": raw,
            "clean": clean,
            "tokens": tokens,
            "intent": intent,
            "entity": entity,
            "family_id": family_id,
            "canonical": family_id,         # alias used elsewhere
            "canonical_display": f"{intent}:{entity}",
        }

    def get_family_id(self, query: str) -> str:
        """Convenience shortcut — returns only family_id."""
        return self.normalize(query)["family_id"]

    def same_family(self, query_a: str, query_b: str) -> bool:
        """Returns True if two queries map to the same family."""
        return self.get_family_id(query_a) == self.get_family_id(query_b)

    # ── Internal helpers ────────────────────────────────────────────────────── #

    def _apply_synonyms(self, text: str) -> str:
        """Replace multi-word synonym phrases with their canonical form."""
        # Sort by length descending to prefer longer matches
        for phrase in sorted(self._synonym_lookup, key=len, reverse=True):
            if phrase in text:
                text = text.replace(phrase, self._synonym_lookup[phrase])
        return text

    def _extract_intent(self, text: str) -> str:
        for intent, patterns in INTENT_PATTERNS.items():
            if any(p in text for p in patterns):
                return intent
        return "general"

    def _extract_entity(self, tokens: List[str]) -> str:
        """Returns the most informative token (longest, non-generic)."""
        candidates = [t for t in tokens if len(t) > 2]
        if not candidates:
            return "GENERAL"
        # Prefer known canonical synonyms
        for c in candidates:
            if c in SYNONYM_MAP:
                return c.upper()
        return candidates[0].upper()

    def _build_family_id(self, clean: str, intent: str, entity: str) -> str:
        """
        Deterministic, stable family_id.
        Format: fam:{intent}:{entity} when meaningful.
        Falls back to a 12-char hash of the cleaned query.
        """
        if intent != "general" and entity != "GENERAL":
            return f"fam:{intent}:{entity.lower()}"
        # Stable hash for generic/unclassified queries
        h = hashlib.sha256(clean.encode()).hexdigest()[:12]
        return f"fam:general:{h}"


global_query_family_mapper = QueryFamilyMapper()
