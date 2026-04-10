"""
Query Shaping Engine
Converts ALL queries into a canonical structured form.
Collapses phrasing variations — "what is X" / "define X" / "explain X" → identical shape.
Removes randomness, normalizes variations, enables maximum cache hits.
"""
import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Maps synonym phrases → canonical intent
INTENT_NORMALIZATION = {
    "definition": [
        r"what is\b", r"what are\b", r"\bdefine\b", r"\bdefinition of\b",
        r"\bmeaning of\b", r"\bwhat does .+ mean\b",
    ],
    "how_to": [
        r"how (do|does|can|to|should) (i|we|you|one)?\b", r"steps to\b",
        r"guide (to|for)\b", r"tutorial (on|for)\b", r"way to\b",
    ],
    "comparison": [
        r"\bvs\.?\b", r"\bversus\b", r"\bcompare\b", r"\bdifference between\b",
        r"\bbetter than\b", r"\bor\b.+\bwhich\b",
    ],
    "explanation": [
        r"\bwhy\b", r"\bhow (does|do)\b", r"\bexplain\b", r"\bunderstand\b",
        r"\breason (for|behind|why)\b",
    ],
    "list": [
        r"\blist\b", r"\bname\b", r"\bgive examples\b", r"\btypes of\b",
        r"\bexamples of\b",
    ],
    "calculation": [
        r"\d+\s*[\+\-\*\/]\s*\d+", r"\bcalculate\b", r"\bcompute\b",
        r"\bsolve\b", r"\bwhat is \d+",
    ],
}

# Canonical entity extraction
ENTITY_EXTRACTORS = [
    r"what is (?:a |an |the )?([a-z][a-z0-9\-]+)",
    r"define (?:a |an |the )?([a-z][a-z0-9\-]+)",
    r"explain (?:a |an |the )?([a-z][a-z0-9\-]+)",
    r"how (?:does|do) ([a-z][a-z0-9\-]+)",
    r"(?:vs\.?|versus|compare) ([a-z][a-z0-9\-]+)",
]

FILLER_WORDS = re.compile(
    r"\b(please|kindly|can you|could you|would you|i want to|i need to|help me|tell me|"
    r"i was wondering|do you know|i'd like to know|could someone explain)\b",
    re.IGNORECASE,
)


class QueryShaper:
    """
    Converts free-form queries into canonical structured form.
    Identical shaped queries always hit the same cache/graph entry.
    """

    def shape(self, query: str) -> Dict[str, Any]:
        """Returns canonical {intent, entity, complexity, canonical_text, shape_key}"""
        # Step 1: Clean
        cleaned = FILLER_WORDS.sub("", query).strip()
        cleaned = re.sub(r"\s+", " ", cleaned).strip("?. ")
        cleaned = cleaned.lower()

        # Step 2: Extract intent
        intent = self._normalize_intent(cleaned)

        # Step 3: Extract entity
        entity = self._extract_entity(cleaned)

        # Step 4: Complexity
        word_count = len(cleaned.split())
        complexity = "low" if word_count < 8 else ("high" if word_count > 20 else "medium")

        # Step 5: Canonical text — deterministic representation
        canonical = f"{intent}:{entity}"

        # Step 6: Shape key — used as cache/graph lookup key
        shape_key = f"{intent}#{entity.replace(' ', '_')}"

        result = {
            "original": query,
            "cleaned": cleaned,
            "intent": intent,
            "entity": entity,
            "complexity": complexity,
            "canonical": canonical,
            "shape_key": shape_key,
        }
        logger.debug(f"query_shaped: {shape_key}")
        return result

    def _normalize_intent(self, query: str) -> str:
        for intent, patterns in INTENT_NORMALIZATION.items():
            for p in patterns:
                if re.search(p, query):
                    return intent
        return "general"

    def _extract_entity(self, query: str) -> str:
        for pattern in ENTITY_EXTRACTORS:
            m = re.search(pattern, query)
            if m:
                return m.group(1).strip().upper()
        # Fallback: longest word that looks like a technical term
        words = [w for w in query.split() if len(w) > 3 and w.isalpha()]
        return words[0].upper() if words else "GENERAL"

    def shape_key(self, query: str) -> str:
        """Quick shortcut to get just the shape_key."""
        return self.shape(query)["shape_key"]


global_query_shaper = QueryShaper()
