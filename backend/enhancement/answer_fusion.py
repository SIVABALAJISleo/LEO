"""
Answer Fusion Engine
Combines outputs from multiple sources (Cache, RAG, Graph) into a single cohesive answer.
"""

class AnswerFusion:
    def fuse(self, sources: dict) -> str:
        """
        Combines content from 'cache', 'rag', and 'graph' keys.
        """
        parts = []
        
        # 1. Start with high-confidence cache hit
        if sources.get("cache"):
            parts.append(f"Primary Record: {sources['cache']}")
            
        # 2. Layer in RAG details
        if sources.get("rag"):
            parts.append(f"Retrieved Context: {sources['rag']}")
            
        # 3. Add Graph relationships
        if sources.get("graph"):
            parts.append(f"Linked Knowledge: {sources['graph']}")
            
        if not parts:
            return ""
            
        return "\n\n".join(parts)

global_answer_fusion = AnswerFusion()
