import logging
from typing import List, Dict, Any, Optional, Tuple
from hybrid_intel_ai.knowledge import VerifiedKnowledgeLayer

logger = logging.getLogger(__name__)

class HyperMemory:
    """
    LAYER 2 & 4: CONTEXT AS MEMORY & RAG
    Treats the context window as working RAM and manages FAISS grounding.
    """
    def __init__(self, knowledge_layer: VerifiedKnowledgeLayer):
        self.rag = knowledge_layer
        self.scratchpad: Dict[str, Any] = {
            "goal": "",
            "subtasks": [],
            "results": {},
            "critique": "",
            "final_output": ""
        }

    def reset(self):
        self.scratchpad = {"goal": "", "subtasks": [], "results": {}, "critique": "", "final_output": ""}

    def get_scratchpad_string(self) -> str:
        s = "--- STRUCTURED SCRATCHPAD ---\n"
        s += f"[GOAL]: {self.scratchpad['goal']}\n"
        s += f"[SUBTASKS]: {', '.join(self.scratchpad['subtasks'])}\n"
        for k, v in self.scratchpad['results'].items():
            s += f"[RESULT - {k}]: {v}\n"
        if self.scratchpad['critique']:
            s += f"[CRITIQUE]: {self.scratchpad['critique']}\n"
        return s

    def retrieve(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        return self.rag.retrieve_with_source(query)
