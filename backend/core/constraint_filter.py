"""
backend/core/constraint_filter.py

Constraint Filter Engine (AIS++ Module 15)
===========================================
Enforces strict correctness on candidate results.
Eliminates invalid semantic matches before they reach assembly.
Anchors keywords to prevent "hallucination-by-similarity".

Rules:
- No approximate answer without validation.
- Anchor keywords (nouns/entities) must match.
- Domain-specific constraints (numbers/dates/units) enforced.
"""
import logging
import re
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class ConstraintFilter:
    """
    Validates candidate answers against query constraints.
    Prevents weak similarity hits from becoming final answers.
    """
    def __init__(self):
        # Domain triggers -> required patterns in answer
        self._domain_constraints = {
            "price": [r"\d+", r"[\$€£]|rupees|usd"],
            "date": [r"\d{4}", r"jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"],
            "calculation": [r"\d+", r"=", r"\+|-|\*|/"]
        }

    def validate(self, query: str, answer: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates an answer against query 'anchors' and domain constraints.
        Returns (is_valid, reason).
        """
        # 1. ANCHOR KEYWORD CHECK (Most Critical)
        # Extract nouns/entities from query (simple regex for now)
        anchors = re.findall(r'\b[A-Z][a-z0-9]+\b|\b\d{2,}\b', query) # Proper nouns or long numbers
        for anchor in anchors:
            if anchor.lower() not in answer.lower():
                logger.warning(f"constraint_filter: REJECTED hit. Missing anchor '{anchor}'")
                return False, f"missing_anchor_{anchor}"

        # 2. DOMAIN CONSTRAINT ENFORCEMENT
        query_lower = query.lower()
        for domain, patterns in self._domain_constraints.items():
            if domain in query_lower:
                for pattern in patterns:
                    if not re.search(pattern, answer.lower()):
                        logger.warning(f"constraint_filter: REJECTED hit. Violates domain '{domain}' pattern '{pattern}'")
                        return False, f"domain_violation_{domain}"

        # 3. ENTITY OVERLAP (If provided in context)
        entity = context.get("entity")
        if entity and entity.lower() not in answer.lower().replace(" ", "_"):
            # Check for partial match if entity is snake_case
            parts = entity.lower().split("_")
            if not any(p in answer.lower() for p in parts):
                logger.warning(f"constraint_filter: REJECTED hit. Entity mismatch '{entity}'")
                return False, "entity_mismatch"

        return True, "valid"

global_constraint_filter = ConstraintFilter()
