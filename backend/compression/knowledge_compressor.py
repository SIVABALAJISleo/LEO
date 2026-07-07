import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class KnowledgeCompressor:
    """
    Converts full natural language answers into a structured, minimal representation.
    Removes fluff, extracts core concepts, and pre-categorizes intent.
    """
    
    def compress(self, query: str, full_answer: str) -> Dict[str, Any]:
        """
        AI Architect (Point 13): Knowledge Compression.
        Merge similar fragments, remove duplicates, and streamline retrieval.
        """
        # Determine intent heuristically
        intent = "explanation"
        if "step" in query.lower() or "how to" in query.lower():
            intent = "steps"
        elif "vs" in query.lower() or "difference" in query.lower():
            intent = "comparison"
            
        # Basic structural compression (splitting logic)
        lines = [line.strip() for line in full_answer.split('\n') if line.strip()]
        
        # Point 13: Merge similar fragments & remove duplicates
        unique_points = list(set([line for line in lines if len(line) > 15]))
        key_points = self._merge_fragments(unique_points)
        
        compressed = {
            "concept": query,
            "intent": intent,
            "key_points": key_points[:8], # Expanded for better composition
            "entities": self._extract_entities(query),
            "relationships": []
        }
        
        logger.info(f"knowledge_compressed: {query} -> {len(json.dumps(compressed))} bytes")
        return compressed

    def _merge_fragments(self, fragments: List[str]) -> List[str]:
        """Point 13: Merging similar fragments to optimize retrieval speed."""
        if not fragments: return []
        
        merged = []
        
        for f in sorted(fragments, key=len, reverse=True):
            # Check for high overlap with already merged fragments
            is_sub = False
            for m in merged:
                if f in m or (len(set(f.split()) & set(m.split())) / max(len(f.split()), 1) > 0.8):
                    is_sub = True
                    break
            if not is_sub:
                merged.append(f)
        return merged

    def _extract_entities(self, text: str) -> List[str]:
        # Simple extraction
        words = text.split()
        return [w for w in words if w.istitle() and len(w) > 3]

global_knowledge_compressor = KnowledgeCompressor()
