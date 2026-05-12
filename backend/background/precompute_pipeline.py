"""
backend/background/precompute_pipeline.py
Precomputation Pipeline.

Executes full LLM resolution offline and populates stores.
"""
import logging
from backend.models.llm_loader import generate_response
from backend.rag.embedding_model import search as rag_search
from backend.intelligence.delta_engine import global_delta_engine_v2
from backend.compression.fragments import global_fragment_compressor
from backend.shadow.shadow_store import global_shadow_store

logger = logging.getLogger(__name__)

class PrecomputePipeline:
    async def resolve_and_store(self, query: str, tenant_id: str, workspace_id: str, session_id: str):
        """
        Runs the full (heavy) resolution for a query offline and stores it.
        """
        logger.info(f"bg_precompute: Resolving query='{query}'")
        
        try:
            # 1. Check if already known
            delta = global_delta_engine_v2.find_delta(query)
            if delta and delta["mode"] == "FULL_MATCH":
                logger.debug(f"bg_precompute: Query already known='{query}'")
                return

            # 2. Full RAG Context
            context_nodes = rag_search(query, k=3)
            context_str = "\n".join([n["content"] for n in context_nodes])
            
            system_prompt = (
                "You are a precomputation bot. Answer precisely based on context.\n"
                f"Context: {context_str}"
            )
            
            # 3. Heavy Generation (Offline)
            import asyncio
            loop = asyncio.get_event_loop()
            answer = await loop.run_in_executor(
                None, generate_response, query, 512, 0.7, system_prompt
            )
            
            # 4. Store in all high-speed layers
            # Layer 0: Shadow Store (Context-sensitive prediction)
            global_shadow_store.register(query, answer, session_id, tenant_id, workspace_id)
            
            # Layer 1: Delta Engine (Semantic Cache)
            global_delta_engine_v2.register_answer(query, answer)
            
            # Layer 2: Fragment Storage
            global_fragment_compressor.fragmentize_and_store(answer)
            
            logger.info(f"bg_precompute: Successfully pre-cached result for '{query}'")
            return {"answer": answer, "source": "BG_PRECOMPUTE"}
            
        except Exception as e:
            logger.error(f"bg_precompute: Resolution error for '{query}' - {e}")
            return None

global_precompute_pipeline = PrecomputePipeline()
