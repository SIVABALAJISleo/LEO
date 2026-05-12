"""
Query Complexity Estimator
Classifies queries as simple / medium / complex to route them efficiently.
Simple queries skip the model entirely.
"""
import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

SIMPLE_INDICATORS = {
    "intents": {"definition", "calculation"},
    "max_words": 8,
    "patterns": [r"^what is \w+\??$", r"^\d+\s*[\+\-\*\/]\s*\d+$"],
}

COMPLEX_INDICATORS = {
    "min_words": 20,
    "keywords": [
        "compare", "analyze", "architect", "design", "explain in detail",
        "tradeoffs", "implementation", "advantages and disadvantages",
        "step by step", "comprehensive"
    ]
}


class QueryComplexityEstimator:
    """
    Lightweight complexity classification — no model calls required.
    Routes simple queries directly to templates/cache, skipping inference.
    """

    def estimate(self, query: str, normalized: Optional[Dict[str, Any]] = None) -> str:
        """Returns 'simple', 'medium', or 'complex'."""
        q = query.lower().strip()
        word_count = len(q.split())

        # Rule 1: Explicit simple patterns
        for p in SIMPLE_INDICATORS["patterns"]:
            if re.match(p, q):
                logger.debug("complexity=simple (pattern_match)")
                return "simple"

        # Rule 2: Intent-based simple
        if normalized:
            intent = normalized.get("intent")
            if intent in SIMPLE_INDICATORS["intents"] and word_count <= SIMPLE_INDICATORS["max_words"]:
                logger.debug(f"complexity=simple (intent={intent})")
                return "simple"

        # Rule 3: Complex keywords
        if any(kw in q for kw in COMPLEX_INDICATORS["keywords"]):
            logger.debug("complexity=complex (keyword_match)")
            return "complex"

        # Rule 4: Word count
        if word_count >= COMPLEX_INDICATORS["min_words"]:
            logger.debug(f"complexity=complex (word_count={word_count})")
            return "complex"

        logger.debug(f"complexity=medium (word_count={word_count})")
        return "medium"

    def should_skip_model(self, complexity: str) -> bool:
        """Simple queries always skip the model."""
        return complexity == "simple"


global_complexity_estimator = QueryComplexityEstimator()
