"""
backend/intelligence/domain_expander.py
Unknown Domain Expansion Engine

Preemptively generates dimensions of a brand new topic (definitions, examples)
and stores them immediately so the next query on this topic isn't "unknown".
"""
import logging
import asyncio
from typing import Dict, Any
from backend.rag.embedding_model import index_documents
from backend.models.llm_loader import generate_response
from backend.intelligence.delta_engine import global_delta_engine_v2

logger = logging.getLogger(__name__)

class DomainExpander:
    async def expand_and_store(self, query: str, decomposed: Dict[str, Any], tenant_id: str = "default"):
        """
        Background task: Once an unknown query goes through the fallback model,
        we expand its entities to seed the RAG and fragment stores.
        """
        logger.info("domain_expander: Expanding unknown domain...")
        
        entities = decomposed.get("entities", [])
        if not entities:
            return
            
        primary_entity = entities[0]
        logger.info(f"domain_expander: Generating background knowledge for '{primary_entity}'")
        
        # 1. Generate foundational knowledge
        try:
            loop = asyncio.get_event_loop()
            system_prompt = "You are a factual knowledge generator. Provide a brief definition followed by 2 examples."
            prompt = f"Provide a definition and 2 examples for: {primary_entity}"
            
            expansion = await loop.run_in_executor(
                None, generate_response, prompt, 256, 0.4, system_prompt
            )
            
            # 2. Store in Delta Engine to cache the semantic cluster
            expanded_query = f"what is {primary_entity} give examples"
            global_delta_engine_v2.register_answer(expanded_query, expansion)
            
            # 3. Store in Vector DB to ensure future composability
            docs_to_index = [
                f"Definition of {primary_entity}: " + expansion.split('\n')[0],
                f"Examples and context for {primary_entity}: " + expansion
            ]
            
            index_documents(docs_to_index, tenant_id=tenant_id)
            logger.info(f"domain_expander: Successfully established permanent knowledge for '{primary_entity}'")
            
        except Exception as e:
            logger.error(f"domain_expander: Expansion failed - {e}")

global_domain_expander = DomainExpander()
