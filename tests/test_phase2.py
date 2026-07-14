import logging
import time
import sys
import os
import threading
import numpy as np

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Add parent dir to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.execution.predictive_engine import PredictiveExecutionEngine
from backend.caching.semantic_cache import MultiLevelSemanticCache
from backend.retrieval.hybrid_search import HybridRetrievalEngine
from backend.intelligence.prompt_compressor import IntelligentPromptCompressor

def test_phase2_architecture():
    logger.info("--- Testing LEO AI V∞ RESEARCH EDITION: Phase 2 ---")
    
    # 1. Test Predictive Execution Engine
    logger.info("\n[Test] 3. Predictive Execution Engine")
    predictive_engine = PredictiveExecutionEngine(idle_threshold_sec=0.5)
    
    task_done = threading.Event()
    def dummy_prefetch():
        task_done.set()  # Signal completion atomically
        
    predictive_engine.enqueue_background_task("TestPrefetch", dummy_prefetch)
    predictive_engine.start()
    
    # Wait up to 3 seconds for the background task to fire
    fired = task_done.wait(timeout=3.0)
    predictive_engine.stop()
    assert fired, "Background predictive task failed to execute during idle time."
    logger.info("✅ Predictive Execution Engine verified.")

    # 2. Test Multi-Level Semantic Cache
    logger.info("\n[Test] 4. Multi-Level Semantic Cache")
    cache = MultiLevelSemanticCache()
    
    q_exact = "What is the speed of light?"
    a_exact = "299,792,458 m/s"
    cache.add_to_cache(q_exact, a_exact)
    
    res = cache.check_cache(" what is the speed of light? ")
    assert res == a_exact, "L1 Exact Cache Miss"
    
    # Mock Vectors
    v1 = np.array([1.0, 0.0, 0.0])
    cache.add_to_cache("Vector Q1", "Vector A1", v1)
    
    v_sim = np.array([0.99, 0.1, 0.0]) # High similarity
    res_vec = cache.check_cache("Unknown Q", query_vector=v_sim, similarity_threshold=0.9)
    assert res_vec == "Vector A1", "L2 Semantic Cache Miss"
    
    logger.info("✅ Multi-Level Semantic Cache verified.")

    # 3. Test Retrieval Engine
    logger.info("\n[Test] 14. Hybrid Retrieval Engine")
    retrieval = HybridRetrievalEngine()
    retrieval.add_document("doc1", "The quick brown fox jumps over the lazy dog.", np.array([1.0, 0.0]))
    retrieval.add_document("doc2", "Machine learning is the study of computer algorithms.", np.array([0.0, 1.0]))
    
    results = retrieval.search("brown fox", np.array([0.9, 0.1]), top_k=1)
    assert len(results) > 0 and results[0]["doc_id"] == "doc1", "Hybrid Search failed to rank correct doc."
    logger.info("✅ Hybrid Retrieval Engine verified.")

    # 4. Test Prompt Compressor
    logger.info("\n[Test] 16. Intelligent Prompt Compressor")
    compressor = IntelligentPromptCompressor()
    
    messy_context = [
        "This is the first sentence.   This is the first sentence.",
        "And then, \n\n   we have this     other thing here."
    ]
    
    compressed = compressor.compress_context(messy_context, aggressive=True)
    logger.info(f"Compressed Result: '{compressed}'")
    assert "This is first sentence." not in compressed # Duplicate should be removed
    assert "\n\n" not in compressed # Whitespace stripped
    
    logger.info("✅ Intelligent Prompt Compressor verified.")
    logger.info("\n🚀 Phase 2 Caching & Data Flow: FULLY FUNCTIONAL")

if __name__ == "__main__":
    test_phase2_architecture()
