import asyncio
import time
import logging
from backend.core.orchestrator import hyper_engine
from backend.shadow.shadow_store import global_shadow_store
from backend.predictive.answer_store import global_predictive_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def benchmark_predictive_hits():
    tenant_id = "test_tenant"
    session_id = "test_session"
    query = "What is the capital of France?"
    answer = "Paris"

    # 1. Warm up Stores
    global_predictive_store.save_answer(query, answer, 0.99, tenant_id=tenant_id)
    global_shadow_store.save_shadow("What happens next?", "Next event", 0.99, session_id, tenant_id)

    # 2. Measure Predictive Latency
    logger.info("--- Starting PPE Benchmark ---")
    start = time.time()
    result = await hyper_engine.process(query, "req_1", tenant_id=tenant_id)
    latency = (time.time() - start) * 1000
    logger.info(f"PPE Hit Latency: {latency:.2f}ms (Target: <20ms)")
    logger.info(f"Mode: {result['mode']}")

    # 3. Measure Shadow Latency
    logger.info("--- Starting Shadow Benchmark ---")
    start = time.time()
    result = await hyper_engine.process("What happens next?", f"req_{session_id}", tenant_id=tenant_id)
    latency = (time.time() - start) * 1000
    logger.info(f"Shadow Hit Latency: {latency:.2f}ms (Target: <20ms)")
    logger.info(f"Mode: {result['mode']}")

if __name__ == "__main__":
    from backend.core.database import init_db
    init_db()
    asyncio.run(benchmark_predictive_hits())
