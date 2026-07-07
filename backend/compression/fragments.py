"""
backend/compression/fragments.py
Fragment Compression Engine: breaks complex answers into specific intents
(definition, steps, examples, advantages) to be reused individually.
"""
import hashlib
import logging
import re
from typing import List

logger = logging.getLogger(__name__)

class FragmentCompressor:
    """Chunks answers into semantic intents and stores them by ID."""
    def __init__(self):
        self._fragment_store = {}  # In-memory mapping

    def _identify_intent(self, text: str) -> str:
        t = text.lower()
        if any(w in t for w in ["step", "first", "second", "then", "finally", "1.", "2."]):
            return "steps"
        if any(w in t for w in ["example", "for instance", "such as", "like"]):
            return "examples"
        if any(w in t for w in ["advantage", "benefit", "pros", "reduce", "improve", "faster"]):
            return "advantages"
        return "definition"

    def fragmentize_and_store(self, text: str) -> List[str]:
        """Splits answer by newlines/paragraphs, categorizes, and registers them."""
        fragments = []
        parts = re.split(r'\n{2,}', text.strip())
        if len(parts) == 1:
            parts = re.split(r'(?<=[.!?])\s+', text.strip())
            
        for part in parts:
            part = part.strip()
            if len(part) < 10:
                continue
            intent = self._identify_intent(part)
            f_hash = hashlib.sha256(part.encode()).hexdigest()[:12]
            f_id = f"frag_{intent}_{f_hash}"
            if f_id not in self._fragment_store:
                self._fragment_store[f_id] = part
            fragments.append(f_id)
            
        logger.info("fragmentized: created/reused %d fragments from answer.", len(fragments))
        return list(dict.fromkeys(fragments))  # remove duplicates

    def assemble(self, fragment_ids: List[str]) -> str:
        """Reassembles an answer from a list of fragment IDs."""
        resolved = []
        for fid in fragment_ids:
            if fid in self._fragment_store:
                resolved.append(self._fragment_store[fid])
        return "\n\n".join(resolved)

global_fragment_compressor = FragmentCompressor()