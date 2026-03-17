import os
import logging
from celery import Celery
import asyncio
from backend.core.orchestrator import hyper_engine
from backend.core.database import SessionLocal, DocumentMetadata

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "hyper_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

class BatchInferenceManager:
    """Aggregates multiple AI requests for batched processing (Hyperscale Pattern)."""
    def __init__(self, batch_size=4):
        self.batch_size = batch_size
        self.current_batch = []
    
    async def add_to_batch(self, query: str):
        self.current_batch.append(query)
        if len(self.current_batch) >= self.batch_size:
            return await self.process_batch()
        return None

    async def process_batch(self):
        # In a real system, this would call model.generate_batch
        logger.info(f"processing_inference_batch: size={len(self.current_batch)}")
        results = [f"Batch result for: {q}" for q in self.current_batch]
        self.current_batch = []
        return results

batch_manager = BatchInferenceManager()

@celery_app.task(name="process_ai_query")
def process_ai_query_task(query: str, request_id: str, tenant_id: str = "default"):
    """
    Background task for AI orchestration with tenant isolation.
    """
    loop = asyncio.get_event_loop()
    if loop.is_running():
        future = asyncio.run_coroutine_threadsafe(hyper_engine.process(query, request_id, tenant_id), loop)
        return future.result()
    else:
        return asyncio.run(hyper_engine.process(query, request_id, tenant_id))

@celery_app.task(name="ingest_document")
def ingest_document_task(text: str, filename: str, user_id: str, tenant_id: str = "default"):
    """
    Background task for RAG ingestion with tenant metadata.
    """
    asyncio.run(hyper_engine.rag.add_documents([text], tenant_id=tenant_id))
    
    # Store metadata for durability
    db = SessionLocal()
    try:
        # Link metadata to the correct tenant
        meta = DocumentMetadata(filename=filename, user_id=0, tenant_id=tenant_id, content_hash=str(hash(text)))
        db.add(meta)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to store doc metadata: {e}")
    finally:
        db.close()
    
    return {"status": "ingested", "filename": filename}
