"""
backend/core/atomic_stitcher.py

Atomic Stitcher Engine (AIS++ Module 10)
=========================================
Replaces heavy AI generation with atomic retrieval + assembly.
Stores knowledge as small "atoms" (3–10 word logic units).
Assembles final answers using bitwise hashes and string templates.

GHOST LEARNING: Spontaneously fragments answers into atoms during idle time.
"""
import logging
import time
import re
import hashlib
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Atomic constraints
MIN_ATOM_WORDS = 3
MAX_ATOM_WORDS = 10

class AtomicStitcher:
    """
    Retrieves and stitches 'atoms' into a coherent response.
    Zero matrix compute. Pure lookup and string assembly.
    """
    def __init__(self):
        # atom_hash -> {text, context_tags}
        self._atom_store: Dict[str, Dict[str, Any]] = {}

    def store_atoms(self, text: str, tags: Optional[List[str]] = None) -> int:
        """Fragments text into atoms and stores them."""
        # Split by periods, semicolons, or double newlines
        segments = re.split(r'[.;\n]\s*', text)
        count = 0
        for seg in segments:
            seg = seg.strip()
            words = seg.split()
            if MIN_ATOM_WORDS <= len(words) <= MAX_ATOM_WORDS:
                ahash = self._hash(seg)
                if ahash not in self._atom_store:
                    self._atom_store[ahash] = {
                        "text": seg,
                        "tags": tags or [],
                        "ts": time.time()
                    }
                    count += 1
        return count

    def assemble(self, query: str, entity: str, intent: str) -> Optional[str]:
        """
        Attempts to find atoms matching entity/intent and query keywords.
        Stitches them using a simple template.
        """
        keywords = set(re.findall(r'\w+', query.lower()))
        entity_lower = entity.lower()
        
        # 1. FIND MATCHING ATOMS (Bitwise-ready hash lookup / Exact match)
        # In a real bitwise system, we'd use XOR/Hamming on bitsets.
        # Here we simulate with a keyword filter.
        candidates = []
        for a in self._atom_store.values():
            if entity_lower in a["text"].lower() or any(t.lower() == entity_lower for t in a["tags"]):
                # Keyword overlap score
                overlap = len(keywords.intersection(set(re.findall(r'\w+', a["text"].lower()))))
                if overlap > 0:
                    candidates.append((overlap, a["text"]))
        
        if not candidates:
            return None
            
        # Sort by overlap DESC
        candidates.sort(key=lambda x: x[0], reverse=True)
        top_atoms = [c[1] for c in candidates[:4]] # Limit to 4 atoms
        
        # 2. STITCH VIA TEMPLATE (Template Transform Engine)
        if intent == "definition":
            template = "{entity} is defined by several key attributes. {atoms} This covers the primary logical units."
        elif intent == "how_to":
            template = "To implement {entity}, consider these atomic steps: {atoms}"
        else:
            template = "Regarding {entity}: {atoms}"
            
        # Assembly
        joined = " ".join([a.capitalize().rstrip('.') + "." for a in top_atoms])
        answer = template.format(entity=entity.replace("_", " "), atoms=joined)
        
        logger.info(f"atomic_stitcher.assembled: query='{query}' atoms={len(top_atoms)}")
        return answer

    def _hash(self, text: str) -> str:
        """Fast bitwise-friendly fingerprint."""
        return hashlib.sha256(text.lower().encode()).hexdigest()[:12]

    def stats(self) -> Dict[str, Any]:
        return {
            "atom_count": len(self._atom_store),
            "status": "ready_for_assembly"
        }

global_atomic_stitcher = AtomicStitcher()
