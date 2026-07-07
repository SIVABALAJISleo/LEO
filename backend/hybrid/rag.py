import chromadb
import logging
import httpx
from typing import List

logger = logging.getLogger(__name__)

class RAGPipeline:
    """
    Module 3: SLOW PATH -> RAG PIPELINE
    Vector DB: Chroma
    Optional: Web Search (Tavily)
    """
    def __init__(self, collection_name: str = "hybrid_collection"):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.tavily_api_key = "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" # Placeholder

    async def retrieve(self, query: str, k: int = 3) -> List[str]:
        """Fetch top-k chunks from Chroma."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )
            return results.get("documents", [[]])[0]
        except Exception as e:
            logger.error(f"Chroma retrieval failed: {e}")
            return []

    async def web_search(self, query: str) -> List[str]:
        """Fetch results from web search (Tavily)."""
        # In a real app, we'd use the Tavily Python SDK or httpx
        # For now, it's a mock if API key is placeholder
        if not self.tavily_api_key.startswith("tvly-actual"):
            return ["Web search results omitted (API key required)"]
            
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.tavily.com/search",
                    json={"api_key": self.tavily_api_key, "query": query}
                )
                data = resp.json()
                return [r["content"] for r in data.get("results", [])]
        except Exception as e:
            logger.warning(f"Web search failed: {e}")
            return []

    async def get_context(self, query: str) -> str:
        """Combine local RAG and Web Search contexts."""
        local_chunks = await self.retrieve(query)
        # Only web search if local context is sparse
        web_chunks = []
        if len(local_chunks) < 1:
            web_chunks = await self.web_search(query)
            
        combined = local_chunks + web_chunks
        return "\n\n".join(combined) if combined else "No relevant context found."

global_rag_pipeline = RAGPipeline()
