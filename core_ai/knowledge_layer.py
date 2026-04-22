import chromadb
from typing import Dict, Any, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

class KnowledgeLayer:
    """
    LAYER 3: KNOWLEDGE LAYER (3-TIER ONLY)
    - Tier 1: Cache (In-memory)
    - Tier 2: Vector DB (Chroma)
    - Tier 3: Live retrieval (Mocked Web/API)
    """
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialize Vector DB (Tier 2)
        try:
            self.chroma = chromadb.Client()
            self.collection = self.chroma.get_or_create_collection(name="core_knowledge")
            # Seed basic knowledge
            self.collection.add(
                documents=["System status is nominally stable.", "Reactor protocols require authorization level Alpha."],
                metadatas=[{"source": "internal_db"}, {"source": "security_manual"}],
                ids=["k1", "k2"]
            )
        except Exception as e:
            logger.error(f"Failed to initialize Vector DB: {e}")
            self.collection = None

    async def retrieve(self, query: str) -> Dict[str, Any]:
        # Tier 1: Cache
        if query in self.cache:
            return {"source": "Tier1_Cache", "data": self.cache[query]}

        # Tier 2: Vector DB
        if self.collection:
            results = self.collection.query(query_texts=[query], n_results=1)
            if results['documents'] and results['distances'][0][0] < 0.5:
                data = results['documents'][0][0]
                self.cache[query] = data  # Update cache
                return {"source": "Tier2_VectorDB", "data": data}

        # Tier 3: Live Retrieval (Stub)
        logger.info(f"Escalating to Tier 3 Live Retrieval for: {query}")
        await asyncio.sleep(0.1) # Simulate network call
        data = f"Live retrieved data for '{query}'"
        self.cache[query] = data
        return {"source": "Tier3_Live", "data": data}
