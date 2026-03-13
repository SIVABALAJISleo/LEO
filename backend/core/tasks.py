import os
from celery import Celery
import asyncio
from backend.core.orchestrator import hyper_engine
from backend.core.database import SessionLocal, DocumentMetadata

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

@celery_app.task(name="process_ai_query")
def process_ai_query_task(query: str, request_id: str):
    """
    Background task for AI orchestration.
    Runs the engine's process method in an async loop.
    """
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # This shouldn't happen in a celery worker worker generally, 
        # but handle just in case it's called in a thread with a loop
        future = asyncio.run_coroutine_threadsafe(hyper_engine.process(query, request_id), loop)
        return future.result()
    else:
        return asyncio.run(hyper_engine.process(query, request_id))

@celery_app.task(name="ingest_document")
def ingest_document_task(text: str, filename: str, user_id: str):
    """
    Background task for RAG ingestion.
    """
    asyncio.run(hyper_engine.rag.add_documents([text]))
    
    # Store metadata for durability
    db = SessionLocal()
    try:
        # In a real app, user_id would be an integer link to users table
        meta = DocumentMetadata(filename=filename, user_id=0, content_hash=str(hash(text)))
        db.add(meta)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to store doc metadata: {e}")
    finally:
        db.close()
    
    return {"status": "ingested", "filename": filename}
