import asyncio
import logging
from backend.core.orchestrator import hyper_engine
from backend.answers.canonical_store import global_canonical_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFICATION")

logger.info(f"DIAG: global_canonical_store source={global_canonical_store.__class__.__module__}")
logger.info(f"DIAG: global_canonical_store attrs={dir(global_canonical_store)}")

async def test_compression_layer():
    test_cases = [
        {"query": "What are the exact steps to implement a Vector Database in production?", "desc": "New Complex Query (First Compute Streak)"},
        {"query": "What are the exact steps to implement a Vector Database in production?", "desc": "Exact Repeated Query (Canonical / Cache Hit)"},
        {"query": "How do I deploy a Vector DB in production environments?", "desc": "Semantically Similar Query (Query Compression Hit)"},
    ]

    for i, case in enumerate(test_cases):
        logger.info(f"\n[{i+1}] TESTING: {case['desc']}")
        logger.info(f"QUERY: {case['query']}")
        try:
            response = await hyper_engine.process(case["query"], request_id=f"verify_comp_{i}")
            mode = response.get("mode")
            latency = response.get('latency_ms', 0)
            
            logger.info(f"RESULT MODE: {mode}")
            logger.info(f"LATENCY: {latency}ms")
            
            content = response.get("result", "")
            if isinstance(content, dict):
                 content = content.get("answer", "")
            logger.info(f"OUTPUT PREVIEW: {content[:100]}...\n")
                 
        except Exception as e:
            logger.error(f"FAIL: {case['query']} failed with {e}")

if __name__ == "__main__":
    asyncio.run(test_compression_layer())
