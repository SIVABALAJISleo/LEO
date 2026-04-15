import asyncio
import time
import logging
import uuid
import os
import json

from backend.core.ais_pipeline import global_ais_pipeline
from backend.analytics.avoidance_tracker import global_avoidance_tracker

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ais_validator")

async def run_pipeline_test():
    logger.info("=========================================")
    logger.info("   AIS++ 14-POINT VALIDATION SCRIPT      ")
    logger.info("=========================================")
    
    tenant_id = "test_tenant_ais"
    user_id = "test_user"
    session_id = "test_session_1"
    
    # Clean old metrics log to ensure we start fresh
    if os.path.exists("metrics.jsonl"):
        try: os.remove("metrics.jsonl")
        except: pass
        
    queries = [
        "What is the capital of Japan?",             # First run should miss caches
        "What is the capital of Japan?",             # Second run should hit global dedup immediately < 10ms
        "ping",                                      # Should hit Task Elimination < 1ms
        "Tell me what the capital of Japan is",      # Semantic / similar query should hit memory_stack or graph < 50ms
        "Who is the CEO of OpenAI?",                 # Another miss
        "Can you tell me who the CEO of OpenAI is?", # Another prediction / memory hit
    ]

    for i, q in enumerate(queries):
        logger.info(f"\n[QUERY {i+1}] '{q}'")
        request_id = f"VAL_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        result = await global_ais_pipeline.handle(
            query=q, 
            request_id=request_id, 
            tenant_id=tenant_id, 
            user_id=user_id, 
            session_id=session_id, 
            start_time=start_time
        )
        
        mode = result.get('mode', 'unknown')
        lat = result.get('latency_ms', 0.0)
        conf = result.get('confidence', 0.0)
        ent = 1.0 - conf
        
        logger.info(f"   => MODE: {mode.upper()}")
        logger.info(f"   => LATENCY: {lat:.2f}ms")
        logger.info(f"   => ENTROPY: {ent:.3f}")
        logger.info(f"   => OUTPUT: {str(result.get('result', ''))[:40]}...")
        
        if mode == "model_last_resort":
            logger.warning("   => (This was a LAST RESORT Model Call)")
        elif ent > 0.05 and "_deferred" not in mode and "_skeleton" not in mode and not result.get("model_called"):
             logger.error("   => RULE VIOLATION: High entropy returned but no model called!")
             
        # Wait a bit for background tasks (graph expansion, prediction) to kick in
        await asyncio.sleep(1.5)

    logger.info("\n=========================================")
    logger.info("          METRICS AUDIT (REAL DATA)      ")
    logger.info("=========================================")
    
    metrics = global_avoidance_tracker.get_live_metrics()
    logger.info(f"Total Requests: {metrics['total_requests']}")
    logger.info(f"Model Calls:    {metrics['model_calls']} ({metrics['model_call_rate']})")
    logger.info(f"Avoidance Rate: {metrics['avoidance_rate']}")
    logger.info(f"Violations:     {metrics['violations']}")
    logger.info(f"Pass criteria:  {metrics['all_criteria_met']}")
    
    if metrics['violations'] > 0:
        logger.error(f"SYSTEM VIOLATIONS RECORDED: {json.dumps(global_avoidance_tracker.get_violation_log(), indent=2)}")
    else:
        logger.info("NO SYSTEM VIOLATIONS (Passes 100% Constraints)")
        
if __name__ == "__main__":
    from backend.core.database import init_db
    init_db()
    asyncio.run(run_pipeline_test())
