import logging
from typing import Dict, Optional
from archive_engines.hybrid_intel_ai.knowledge import VerifiedKnowledgeLayer

logger = logging.getLogger(__name__)

class LLMOSMemory:
    """
    LAYER 2: MEMORY SYSTEM (CONTEXT AS RAM)
    - Short-term: rolling context window (managed in reasoning loop)
    - Long-term: vector DB (FAISS)
    """
    def __init__(self, vector_store: VerifiedKnowledgeLayer):
        self.long_term = vector_store
        # Stores intermediate reasoning steps for the current session
        self.scratchpad: Dict[str, str] = {
            "concepts": "",
            "domain_a": "",
            "domain_b": "",
            "relationships": "",
            "synthesis": "",
            "refinement": ""
        }

    def store_fact(self, text: str, source: str):
        self.long_term.seed_with_sources([(text, source)])

    def retrieve_facts(self, query: str) -> Optional[str]:
        doc, _ = self.long_term.retrieve_with_source(query)
        return doc

    def reset_scratchpad(self):
        for key in self.scratchpad:
            self.scratchpad[key] = ""
            
    def get_full_context(self) -> str:
        context = "--- WORKING MEMORY (SCRATCHPAD) ---\n"
        for key, val in self.scratchpad.items():
            if val:
                context += f"[{key.upper()}]: {val}\n"
        return context
