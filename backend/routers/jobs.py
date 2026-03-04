import logging
import uuid
import time
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from backend.routers.apikeys import verify_api_key_or_jwt as verify_token
# Import celery tasks directly to dispatch them
from backend.tasks.llm_tasks import generate_llm_response
from backend.tasks.vision_tasks import detect_objects
from backend.tasks.jepa_tasks import caption_image, compare_images

from celery.result import AsyncResult

from backend.core.middleware import limit_and_quota_check

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs"])

# Mock DB interaction since the user's DB layer (Firebase/Supabase) is highly environment specific
# In production, this would use a Firebase Admin SDK or SQLAlchemy ORM session to persist the job records.
_mock_jobs_db: Dict[str, Dict[str, Any]] = {}

class JobCreateRequest(BaseModel):
    job_type: str # 'llm', 'vision_detect', 'vision_caption', 'jepa_compare'
    parameters: dict

@router.post("/create", dependencies=[Depends(limit_and_quota_check)])
async def create_job(req: JobCreateRequest, request: Request, token: dict = Depends(verify_token)):
    user_id = token.get("uid") or token.get("sub", "anonymous")
    request.state.user_id = user_id # Pass to middleware
    
    celery_task = None
    task_args = ()
    task_kwargs = {}
    
    # 1. Routing the Job to the Correct Celery Queue
    try:
        if req.job_type == "llm":
            if "prompt" not in req.parameters:
                raise ValueError("Missing 'prompt' parameter")
            celery_task = generate_llm_response
            task_kwargs = {
                "prompt": req.parameters["prompt"],
                "max_tokens": req.parameters.get("max_tokens", 512),
                "temperature": req.parameters.get("temperature", 0.7)
            }
            
        elif req.job_type == "vision_detect":
            if "image_base64" not in req.parameters:
                raise ValueError("Missing 'image_base64' parameter")
            celery_task = detect_objects
            task_kwargs = {"image_base64": req.parameters["image_base64"]}
            
        elif req.job_type == "vision_caption":
            if "image_base64" not in req.parameters:
                 raise ValueError("Missing 'image_base64' parameter")
            celery_task = caption_image
            task_kwargs = {"image_base64": req.parameters["image_base64"]}
            
        elif req.job_type == "jepa_compare":
             if "context_base64" not in req.parameters or "target_base64" not in req.parameters:
                 raise ValueError("Missing context or target image parameters")
             celery_task = compare_images
             task_kwargs = {
                 "context_base64": req.parameters["context_base64"],
                 "target_base64": req.parameters["target_base64"]
             }
        else:
            raise HTTPException(status_code=400, detail="Unknown job_type.")
            
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    # 2. Dispatch Task Asynchronously to Redis Queue
    try:
        # .delay() is the synchronous wrapper. We use .apply_async() to pass explicit kwargs if needed
        # In this event, we execute the background trigger immediately.
        result = celery_task.apply_async(kwargs=task_kwargs)
        job_id = result.id
        
        # 3. Create database tracking record
        job_record = {
            "job_id": job_id,
            "user_id": user_id,
            "job_type": req.job_type,
            "status": "queued", # 'queued', 'running', 'completed', 'failed'
            "created_at": time.time(),
            "completed_at": None,
            "result_storage_url": None, # Filled in later by storage engine
            "metrics": {}
        }
        
        # Simulating DB insert
        _mock_jobs_db[job_id] = job_record
        
        return {
            "status": "queued",
            "job_id": job_id,
            "message": "Job successfully handed off to workers."
        }
    except Exception as e:
        logger.error(f"Failed to submit Celery job: {e}")
        raise HTTPException(status_code=500, detail="Distributed task queue error.")

@router.get("/{job_id}")
async def get_job_status(job_id: str, token: dict = Depends(verify_token)):
    user_id = token.get("uid") or token.get("sub", "anonymous")
    
    db_job = _mock_jobs_db.get(job_id)
    if not db_job:
         raise HTTPException(status_code=404, detail="Job not found in database.")
         
    if db_job["user_id"] != user_id:
         raise HTTPException(status_code=403, detail="Unauthorized access to job.")
         
    # Query Celery Backend for live state
    task_res = AsyncResult(job_id)
    
    # Sync states if the task has completed
    if task_res.state == 'SUCCESS' and db_job['status'] != 'completed':
        db_job['status'] = 'completed'
        db_job['completed_at'] = time.time()
        # In a real SaaS, if result is massive, we would have sent it to S3, 
        # but here we attach it to the JSON response for simplicity.
        db_job['result_payload'] = task_res.result
        
    elif task_res.state == 'FAILURE' and db_job['status'] != 'failed':
        db_job['status'] = 'failed'
        db_job['completed_at'] = time.time()
        db_job['error_trace'] = str(task_res.info)
        
    elif task_res.state == 'STARTED' and db_job['status'] != 'running':
        db_job['status'] = 'running'
        
    # Return normalized SaaS status payload
    return {
        "job_id": job_id,
        "job_type": db_job["job_type"],
        "status": db_job["status"],
        "created_at": db_job["created_at"],
        "completed_at": db_job["completed_at"],
        "result": db_job.get("result_payload", None),
        "error": db_job.get("error_trace", None)
    }

@router.get("/user/history")
async def get_job_history(token: dict = Depends(verify_token), limit: int = 50):
    """Retrieve all jobs executed by the calling user."""
    user_id = token.get("uid") or token.get("sub", "anonymous")
    
    # Simulate DB query: SELECT * FROM jobs WHERE user_id = $1 ORDER BY created_at DESC
    user_jobs = [j for j in _mock_jobs_db.values() if j['user_id'] == user_id]
    user_jobs.sort(key=lambda x: x['created_at'], reverse=True)
    
    return {"jobs": user_jobs[:limit]}
