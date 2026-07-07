import logging
from typing import List
from backend.answers.canonical_store import global_canonical_store
from backend.intelligence.rag import RAGEngine

logger = logging.getLogger(__name__)

class KnowledgeExpansionEngine:
    """
    Ensures 'Compute Once, Reuse Forever'.
    When called, it expands a single result into a library of fragments and variations.
    """
    def __init__(self):
        self.rag = RAGEngine()

    async def expand(self, query: str, answer: str, tenant_id: str = "default"):
        """Background task to expand knowledge."""
        logger.info(f"knowledge_expansion_triggered: query={query}")
        
        # 1. Generate variations using a tiny model (if available) or heuristics
        variations = [
            f"What is {query}?",
            f"Explain {query} in detail",
            f"How does {query} work?",
            f"Examples of {query}"
        ]
        
        # 2. Break answer into fragments
        fragments = self._fragmentize(answer)
        
        # 3. Store canonical mapping for all variations
        for var in variations:
            global_canonical_store.register(var, answer) # reuse the base answer
        
        # 4. Inject fragments into RAG for future composition
        await self.rag.add_documents(fragments, tenant_id=tenant_id)
        
        logger.info(f"knowledge_expansion_complete: variations={len(variations)} fragments={len(fragments)}")

    def _fragmentize(self, text: str) -> List[str]:
        """Simple heuristic to break text into logical fragments."""
        # Split by sentences or bullet points
        import re
        sentences = re.split(r'(?<=[.!?]) +', text)
        fragments = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # Also look for bullet points
        bullets = re.findall(r'(?m)^[-*•] +(.*)', text)
        fragments.extend([b.strip() for b in bullets if len(b.strip()) > 10])
        
        return list(set(fragments))

global_knowledge_expander = KnowledgeExpansionEngine()
