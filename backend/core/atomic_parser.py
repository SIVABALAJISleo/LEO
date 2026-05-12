"""
backend/core/atomic_parser.py

Atomic Parser Engine (AIS++ Module 18)
=======================================
Decomposes queries into fundamental logic units (Atoms).
Replaces heavy NLP with keyword -> primitive mapping.

Primal Units:
- Entity   (subject)
- Action   (verb)
- Time     (temporal context)
- Property (adjective/state)
- Relation (linkage)
"""
import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Basic Primitive patterns
TIME_PATTERNS = {
    "1800s": [r"1800s?", r"19th century"],
    "modern": [r"modern", r"now", r"current"],
    "future": [r"future", r"upcoming", r"planned"]
}

ACTION_PATTERNS = {
    "calculate": [r"calculate", r"compute", r"evaluate"],
    "compare":   [r"compare", r"vs", r"versus"],
    "define":    [r"define", r"what is", r"explain"]
}

class AtomicParser:
    """
    Lightweight primitive extraction.
    Transforms raw text into a set of atomic logic units.
    """
    def parse(self, query: str) -> Dict[str, str]:
        """Extracts primitives: [entity, action, time, property, relation]."""
        query = query.lower().strip()
        entities = re.findall(r'\b[A-Z][a-z0-9]+\b', query.title()) # Simple Proper Noun extraction
        
        # 1. Extraction
        time = self._match(query, TIME_PATTERNS) or "present"
        action = self._match(query, ACTION_PATTERNS) or "query"
        entity = entities[0] if entities else "general"
        
        # 2. Logic Bundle
        primitives = {
            "entity": entity,
            "action": action,
            "time":   time,
            "atomic_hash": f"{entity}_{action}_{time}"
        }
        
        logger.debug(f"atomic_parser: query='{query}' -> {primitives}")
        return primitives

    def _match(self, text: str, pattern_dict: Dict[str, List[str]]) -> Optional[str]:
        for key, patterns in pattern_dict.items():
            for p in patterns:
                if re.search(p, text):
                    return key
        return None

global_atomic_parser = AtomicParser()
