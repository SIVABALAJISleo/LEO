import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class KnowledgeCompressor:
    """
    Converts full natural language answers into a structured, minimal representation.
    Removes fluff, extracts core concepts, and pre-categorizes intent.
    """
    
    def compress(self, query: str, full_answer: str) -> Dict[str, Any]:
        """
        Compresses an answer into a structured dictionary.
        In a full implementation, a small LLM or NLP heuristics would extract this.
        """
        # Determine intent heuristically
        intent = "explanation"
        if "step" in query.lower() or "how to" in query.lower():
            intent = "steps"
        elif "vs" in query.lower() or "difference" in query.lower():
            intent = "comparison"
            
        # Basic structural compression (splitting logic)
        lines = [line.strip() for line in full_answer.split('\n') if line.strip()]
        key_points = [line for line in lines if line.startswith('-') or line.startswith('*') or len(line) > 20]
        
        compressed = {
            "concept": query,
            "intent": intent,
            "key_points": key_points[:5], # Keep top 5
            "entities": self._extract_entities(query),
            "relationships": [] # Populated in advanced versions
        }
        
        logger.info(f"knowledge_compressed: {query} -> {len(json.dumps(compressed))} bytes")
        return compressed

    def _extract_entities(self, text: str) -> list:
        # Simple extraction
        words = text.split()
        return [w for w in words if w.istitle() and len(w) > 3]

global_knowledge_compressor = KnowledgeCompressor()
