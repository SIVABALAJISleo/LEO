"""
backend/intelligence/decomposer.py
Query Decomposition Engine

Breaks query into sub-components (entities, intent, subtopics)
using lightweight NLP (regex, heuristics).
"""
import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class QueryDecomposer:
    def __init__(self):
        # Basic stop words to ignore
        self.stop_words = {"a", "an", "the", "in", "on", "at", "to", "for", "with", "by", "of", "and", "or", "is", "are", "what", "how", "why"}

    def decompose(self, query: str) -> Dict[str, Any]:
        """
        Extracts intent, key entities, and subtopics from a raw query.
        """
        query_lower = query.lower()
        
        # 1. Intent extraction
        intent = "information"
        if any(w in query_lower for w in ["how to", "steps", "guide"]):
            intent = "how_to"
        elif any(w in query_lower for w in ["what is", "define", "explain"]):
            intent = "definition"
        elif any(w in query_lower for w in ["why", "advantages", "benefit", "pros"]):
            intent = "reasoning"
        elif any(w in query_lower for w in ["example", "use case"]):
            intent = "example"
            
        # 2. Entity / Keyword extraction
        words = re.findall(r'\b[a-zA-Z0-9-]+\b', query)
        entities = [w for w in words if w.lower() not in self.stop_words and len(w) > 2]
        
        # Deduplicate while preserving order
        seen = set()
        unique_entities = []
        for e in entities:
            if e.lower() not in seen:
                seen.add(e.lower())
                unique_entities.append(e)

        # 3. Subtopics heuristics
        subtopics = []
        if len(unique_entities) > 1:
            subtopics.extend([f"{unique_entities[i]}_{unique_entities[i+1]}" for i in range(len(unique_entities)-1)])

        result = {
            "intent": intent,
            "entities": unique_entities,
            "subtopics": subtopics[:3],
            "is_creative": any(w in query_lower for w in ["create", "generate", "imagine", "design", "invent", "mix", "simulate"])
        }
        logger.info(f"decomposer: Decomposed query intent='{intent}' entities={len(unique_entities)}")
        return result

global_decomposer = QueryDecomposer()
