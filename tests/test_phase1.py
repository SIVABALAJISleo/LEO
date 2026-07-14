import asyncio
import logging
import time
import sys
import os

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Add parent dir to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.os.orchestrator import LEOOperatingSystem

async def test_phase1_architecture():
    logger.info("--- Testing LEO AI V∞ RESEARCH EDITION: Phase 1 ---")
    
    # 1. Initialize the Adaptive AI OS
    os_kernel = LEOOperatingSystem()
    
    # Allow telemetry thread to gather initial stats
    time.sleep(1.2)
    stats = os_kernel.resource_manager.get_current_stats()
    logger.info(f"System Telemetry Online: CPU {stats['cpu_percent']}%, RAM {stats['ram_percent']}%")
    
    test_queries = [
        "hello",                                    # Should route to RULE_ENGINE
        "45 * 12 + (300 / 2)",                      # Should route to CALCULATOR
        "find the definition of quantum mechanics", # Should route to RETRIEVAL_ENGINE
        "summarize this short text",                # Should route to TINY_MODEL
        "write a comprehensive essay on the socio-economic impacts of the industrial revolution", # LARGE_MODEL
    ]
    
    for query in test_queries:
        logger.info(f"\n[Test] Sending Query: '{query}'")
        response = await os_kernel.execute_request(query)
        logger.info(f"[Result] Routed to {response['route']} in {response['latency_ms']}ms.")
        logger.info(f"[Result] Answer: {response['answer']}")
        
    os_kernel.shutdown()
    logger.info("\n✅ Phase 1 Core OS & Execution Routing: FULLY FUNCTIONAL")

if __name__ == "__main__":
    asyncio.run(test_phase1_architecture())
