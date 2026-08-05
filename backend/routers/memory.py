"""
backend/routers/memory.py
Provides the /api/v1/memory endpoints expected by the frontend.
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/api/v1/memory", tags=["Memory (Frontend-Compat)"])

class MemoryPostRequest(BaseModel):
    content: str = Field(..., min_length=1)
    type: str = Field("semantic")

@router.get("")
async def get_memory(type: Optional[str] = Query("semantic")):
    from backend.core.db_utils import get_concurrent_db_connection
    from backend.core.memory_system import MEMORY_DB_PATH
    
    conn = get_concurrent_db_connection(MEMORY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT memory_id, content, confidence, created_at, access_count FROM memory_system WHERE memory_type = ? ORDER BY created_at DESC",
        (type,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "memory_id": row[0],
            "content": row[1],
            "confidence": row[2],
            "created_at": row[3],
            "access_count": row[4]
        })
    return results

@router.post("")
async def post_memory(req: MemoryPostRequest):
    from backend.core.memory_system import global_memory_system
    memory_id, was_new = global_memory_system.store(
        content=req.content,
        memory_type=req.type,
        confidence=0.9
    )
    return {"success": True, "memory_id": memory_id, "was_new": was_new}
