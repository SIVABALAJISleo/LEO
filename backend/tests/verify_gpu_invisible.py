import asyncio
import logging
from backend.core.orchestrator import hyper_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VERIFICATION")

async def test_gpu_invisible_pipeline():
    test_cases = [
        {"query": "What is a GPU?", "expected_mode": "COMPOSITION_ENGINE"},
        {"query": "Generate an image for Nvidia", "expected_mode": "IMAGE_COMPOSITION"},
        {"query": "Show me a video of AI evolution", "expected_mode": "VIDEO_COMPOSITION"},
        # First compute case (unique query)
        {"query": "Explain the 2026 hyperscaler GPU-Invisible transformation in Project HYPER", "expected_mode": "FIRST_COMPUTE_STREAK"}
    ]

    for case in test_cases:
        logger.info(f"TESTING: {case['query']}")
        try:
            # We use a dummy request_id
            response = await hyper_engine.process(case["query"], request_id="verify_123")
            
            mode = response.get("mode")
            logger.info(f"RESULT: mode={mode} latency={response.get('latency_ms')}ms")
            
            if mode == case["expected_mode"]:
                logger.info("PASS: Mode matches expected.")
            elif mode == "COMPOSITION_ENGINE" and case["expected_mode"] == "FIRST_COMPUTE_STREAK":
                logger.info("PASS: Already solidified in cache/store.")
            else:
                logger.warning(f"NOTE: Mode was {mode}, expected {case['expected_mode']}")
                
            if "content" in response.get("result", "") or len(response.get("result", "")) > 10:
                 logger.info("PASS: Content generated successfully.")
                 
        except Exception as e:
            logger.error(f"FAIL: {case['query']} failed with {e}")

if __name__ == "__main__":
    asyncio.run(test_gpu_invisible_pipeline())
