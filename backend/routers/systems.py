"""
backend/routers/systems.py
API endpoints for LEO AI subsystems:
  - Memory System (store, retrieve, decay)
  - Knowledge Graph (add entity, add relationship, query, extract, stats)
  - Security (scan query, scan document, audit log)
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/api/v1/leo", tags=["LEO Subsystems"])


# ── Request Models ───────────────────────────────────────────────────────────

class MemoryStoreRequest(BaseModel):
    content: str = Field(..., min_length=1)
    memory_type: str = Field("episodic", description="episodic|semantic|working|reflection|failure|procedural")
    confidence: float = Field(0.9, ge=0.0, le=1.0)
    tags: Optional[List[str]] = None

class MemoryQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    memory_type: Optional[str] = None
    top_k: int = Field(5, ge=1, le=50)

class EntityRequest(BaseModel):
    name: str = Field(..., min_length=1)
    entity_type: str = Field("CONCEPT")
    properties: Optional[Dict[str, Any]] = None

class RelationshipRequest(BaseModel):
    source: str = Field(..., min_length=1)
    target: str = Field(..., min_length=1)
    rel_type: str = Field("RELATED_TO")
    weight: float = Field(1.0)

class GraphQueryRequest(BaseModel):
    entity: str = Field(..., min_length=1)
    max_hops: int = Field(2, ge=1, le=5)

class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=10)
    source_label: str = Field("document")

class SecurityScanRequest(BaseModel):
    query: str = Field(..., min_length=1)

class DocumentScanRequest(BaseModel):
    text: str = Field(..., min_length=1)
    document_name: str = Field("")


# ── Memory Endpoints ─────────────────────────────────────────────────────────

@router.post("/memory/store")
async def memory_store(request: MemoryStoreRequest):
    from backend.core.memory_system import global_memory_system
    memory_id, was_new = global_memory_system.store(
        content=request.content,
        memory_type=request.memory_type,
        confidence=request.confidence,
        tags=request.tags,
    )
    return {"memory_id": memory_id, "was_new": was_new}

@router.post("/memory/retrieve")
async def memory_retrieve(request: MemoryQueryRequest):
    from backend.core.memory_system import global_memory_system
    results = global_memory_system.retrieve(
        query=request.query,
        memory_type=request.memory_type,
        top_k=request.top_k,
    )
    return {"results": results, "count": len(results)}

@router.post("/memory/decay")
async def memory_decay():
    from backend.core.memory_system import global_memory_system
    deleted = global_memory_system.decay_and_purge()
    return {"purged_entries": deleted}

@router.get("/memory/summary")
async def memory_summary():
    from backend.core.memory_system import global_memory_system
    return global_memory_system.get_summary()


# ── Knowledge Graph Endpoints ────────────────────────────────────────────────

@router.post("/kg/entity")
async def kg_add_entity(request: EntityRequest):
    from backend.core.knowledge_graph import global_knowledge_graph
    entity_id = global_knowledge_graph.add_entity(
        name=request.name,
        entity_type=request.entity_type,
        properties=request.properties,
    )
    return {"entity_id": entity_id, "name": request.name}

@router.post("/kg/relationship")
async def kg_add_relationship(request: RelationshipRequest):
    from backend.core.knowledge_graph import global_knowledge_graph
    rel_id = global_knowledge_graph.add_relationship(
        source_name=request.source,
        target_name=request.target,
        rel_type=request.rel_type,
        weight=request.weight,
    )
    return {"rel_id": rel_id}

@router.post("/kg/query")
async def kg_query(request: GraphQueryRequest):
    from backend.core.knowledge_graph import global_knowledge_graph
    result = global_knowledge_graph.multi_hop_query(
        start_entity=request.entity,
        max_hops=request.max_hops,
    )
    return result

@router.post("/kg/extract")
async def kg_extract(request: ExtractRequest):
    from backend.core.knowledge_graph import global_knowledge_graph
    result = global_knowledge_graph.extract_and_store(
        text=request.text,
        source_label=request.source_label,
    )
    return result

@router.get("/kg/stats")
async def kg_stats():
    from backend.core.knowledge_graph import global_knowledge_graph
    return global_knowledge_graph.get_stats()

@router.post("/kg/validate")
async def kg_validate():
    from backend.core.knowledge_graph import global_knowledge_graph
    return global_knowledge_graph.validate_and_repair()


# ── Security Endpoints ───────────────────────────────────────────────────────

@router.post("/security/scan")
async def security_scan(request: SecurityScanRequest):
    from backend.security.prompt_guard import global_prompt_guard
    return global_prompt_guard.check_query(request.query)

@router.post("/security/scan-document")
async def security_scan_document(request: DocumentScanRequest):
    from backend.security.prompt_guard import global_prompt_guard
    return global_prompt_guard.check_document(request.text, request.document_name)

@router.get("/security/audit")
async def security_audit():
    from backend.security.prompt_guard import global_prompt_guard
    return {
        "recent_events": global_prompt_guard.audit.get_recent(50),
        "stats": global_prompt_guard.audit.get_stats(),
    }
