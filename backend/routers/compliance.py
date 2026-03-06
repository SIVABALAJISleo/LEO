from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Dict, Any
import logging

from backend.core.audit import audit_logger

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/compliance", tags=["Compliance"])

# Mock dependency for verifying admin or authenticated user
async def get_current_user_id() -> str:
    # In production, this decodes the JWT and validates scopes
    return "usr_prod_12345"

class ExportRequest(BaseModel):
    format: str = "json"

@router.post("/export")
async def request_data_export(
    request: ExportRequest, 
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id)
):
    """
    GDPR Article 20: Right to Data Portability.
    Triggers an asynchronous compilation of all user data.
    """
    
    # Record to immutable audit log BEFORE action
    audit_logger.record_event(
        event_type="DATA_ACCESS",
        actor_id=user_id,
        resource=f"user_data:{user_id}",
        action="EXPORT_REQUESTED",
        metadata={"format": request.format}
    )
    
    # Use Celery for heavy data gathering (Mocked here with BackgroundTasks for simplicity if Celery isn't bound)
    from backend.tasks.compliance_tasks import gather_user_data_task
    background_tasks.add_task(gather_user_data_task, user_id)
    
    return {
        "status": "processing", 
        "message": "Data export initiated. You will receive an email wrapper with your archive within 72 hours."
    }

@router.delete("/erase")
async def request_data_erasure(
    user_id: str = Depends(get_current_user_id)
):
    """
    GDPR Article 17: Right to Erasure ('Right to be Forgotten').
    Asynchronously purges database records, cache, and object storage.
    """
    
    audit_logger.record_event(
        event_type="DATA_DESTRUCTION",
        actor_id=user_id,
        resource=f"user_data:{user_id}",
        action="ERASURE_REQUESTED"
    )
    
    from backend.tasks.compliance_tasks import purge_user_data_task
    # Route to Celery
    purge_user_data_task.delay(user_id)
    
    return {
        "status": "accepted",
        "message": "Account scheduled for hard deletion across all global regions."
    }
