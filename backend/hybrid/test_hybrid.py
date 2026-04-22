import asyncio
import logging
import sys
import os

# Ensure we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.hybrid.orchestrator import global_hybrid_system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_hybrid_flow():
    test_queries = [
        "What is RAG?",
        "How to build a production AI system?",
        "abc123xyz" # Low confidence test
    ]
    
    for query in test_queries:
        logger.info(f"\n--- Testing Query: {query} ---")
        result = await global_hybrid_system.process_query(query)
        logger.info(f"Result: {result}")
        
    logger.info("\n--- Testing Stream ---")
    async for part in global_hybrid_system.process_query_stream("Explain embeddings"):
        logger.info(f"Stream Part: {part}")

if __name__ == "__main__":
    asyncio.run(test_hybrid_flow())
