import logging
from typing import List
from backend.intelligence.rag import RAGEngine

logger = logging.getLogger(__name__)

class QuestionExpander:
    """
    Expands canonical questions into related potential queries 
    using Knowledge Graph neighbors and RAG context.
    """
    def __init__(self):
        self.rag = RAGEngine()

    def expand(self, query: str) -> List[str]:
        """
        Generates variations and related questions for a given canonical query.
        """
        expansions = [
            f"Could you explain more about {query}?",
            f"Details regarding {query}",
            f"Summary of {query}"
        ]
        
        # 1. GRAPH LOOKUP (Future expansion)
        # Use KnowledgeGraph to find neighboring entities
        
        return expansions

global_expander = QuestionExpander()
