import chromadb
import logging
import os
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
        # Configure this secret through the deployment environment, never source code.
        self.tavily_api_key = os.getenv("TAVILY_API_KEY", "").strip()

    async def retrieve(self, query: str, k: int = 3) -> List[str]:
        """Fetch top-k chunks from Chroma."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
            )
            return results.get("documents", [[]])[0]
        except Exception as e:
            logger.error("Chroma retrieval failed: %s", e)
            return []

    async def web_search(self, query: str) -> List[str]:
        """Fetch results from web search (Tavily), if configured."""
        if not self.tavily_api_key:
            logger.info("Tavily web search skipped: TAVILY_API_KEY is not configured")
            return []

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    "https://api.tavily.com/search",
                    json={"api_key": self.tavily_api_key, "query": query},
                )
                resp.raise_for_status()
                data = resp.json()
                return [
                    result["content"]
                    for result in data.get("results", [])
                    if isinstance(result, dict) and isinstance(result.get("content"), str)
                ]
        except (httpx.HTTPError, ValueError) as e:
            # Do not log request data or credentials.
            logger.warning("Tavily web search failed: %s", e)
            return []

    async def get_context(self, query: str) -> str:
        """Combine local RAG and Web Search contexts."""
        local_chunks = await self.retrieve(query)
        # Only web search if local context is sparse.
        web_chunks = []
        if not local_chunks:
            web_chunks = await self.web_search(query)

        combined = local_chunks + web_chunks
        return "\n\n".join(combined) if combined else "No relevant context found."


global_rag_pipeline = RAGPipeline()
