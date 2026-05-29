"""
backend/main.py
LEO: Production-Grade Semantic Compute Orchestration API
"""
import time
import logging
import hashlib
import datetime
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from backend.core.leo_orchestrator import global_leo_orchestrator
from backend.core.database import get_db, PolicyDocument, PolicyChunk, PolicyRelationship, AuditProvenanceLog
from backend.core.policy_system import PolicyParser, GovernanceContradictionEngine, GovernanceRouter

# Import OpenAI drop-in gateway and Telemetry instrumentor
from backend.gateway.openai_gateway import router as openai_router
from backend.observability.telemetry import TelemetryInstrumentor


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LEO — Semantic Compute Orchestration System",
    description="10-Layer enterprise intelligence fabric. Retrieval-first. Compute-last.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register drop-in OpenAI-compatible router and Prometheus telemetry instrumentation
app.include_router(openai_router)
TelemetryInstrumentor.instrument_app(app)



# ── Request / Response Models ─────────────────────────────────────────────── #

class OrchestrateRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=8000, description="The user's semantic query.")
    workspace_id: str = Field("default", description="Tenant / workspace identifier.")
    quality_hint: Optional[str] = Field(None, description="Optional quality hint: ultra|balanced|lightweight|emergency")


class StatusResponse(BaseModel):
    status: str
    system: str
    layers: int
    telemetry: dict
    semantic_store_size: int
    fingerprint_store_size: int
    timestamp: float


# ── Core LEO Orchestration Endpoint ──────────────────────────────────────── #

@app.post("/api/v1/leo/orchestrate", tags=["LEO Orchestration"])
async def leo_orchestrate(request: OrchestrateRequest):
    """
    Execute a query through the full 10-layer LEO Semantic Compute Orchestration cascade.

    Layer priority:
      L2 Semantic Memory Cache → L3 Redundancy Elimination → L4 Policy Gate →
      L5 Novelty Firewall → L6 iGPU Mesh → L7 Surrogate Compute → L8 Graphics →
      L9 Adaptive Quality → L10 Observability
    """
    logger.info(f"[LEO] Orchestrating: workspace={request.workspace_id} query_len={len(request.query)}")
    result = await global_leo_orchestrator.execute_semantic_workflow(
        query=request.query,
        context={"workspace_id": request.workspace_id, "quality_hint": request.quality_hint},
    )
    return result


@app.post("/api/v1/leo/query", tags=["LEO Orchestration"])
async def leo_query_alias(request: OrchestrateRequest):
    """Alias for /orchestrate — OpenAI-compatible naming."""
    return await leo_orchestrate(request)


@app.post("/api/v1/query", tags=["LEO Orchestration"])
async def legacy_query(request: OrchestrateRequest):
    """Legacy endpoint for backward compatibility with OrchestrationExplorer."""
    return await leo_orchestrate(request)


# ── Status & Telemetry Endpoints ─────────────────────────────────────────── #

@app.get("/api/v1/leo/status", tags=["Observability"])
async def leo_status():
    """Return full system status and Layer 10 telemetry."""
    status = global_leo_orchestrator.get_system_status()
    status["timestamp"] = time.time()
    return status


@app.get("/api/v1/leo/metrics", tags=["Observability"])
async def leo_metrics():
    """Return Prometheus-compatible metrics snapshot."""
    telemetry = global_leo_orchestrator.l15.get_metrics()
    return {
        "leo_total_requests": telemetry["total_requests"],
        "leo_compute_avoided": telemetry["compute_avoided"],
        "leo_avoidance_rate_pct": telemetry["avoidance_rate_pct"],
        "leo_gpu_watts_saved": telemetry["gpu_watts_saved"],
        "leo_semantic_store_size": len(global_leo_orchestrator.l0._store),
        "leo_fingerprint_store_size": len(global_leo_orchestrator.l5._decisions),
        "leo_layer_hit_distribution": telemetry["layer_hit_distribution"],
        "timestamp": time.time(),
    }


@app.get("/api/v1/compute/telemetry", tags=["Observability"])
async def compute_telemetry():
    """Legacy telemetry endpoint for frontend api.ts compatibility."""
    import psutil
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.1)
    telemetry = global_leo_orchestrator.l15.get_metrics()
    return {
        "cpu": {"average_utilization": cpu},
        "memory": {
            "total_gb": round(mem.total / 1e9, 2),
            "used_gb": round(mem.used / 1e9, 2),
            "percent_used": mem.percent,
        },
        "leo": telemetry,
        "timestamp": time.time(),
    }


# ── Policy Governance & Relationship API Endpoints ──────────────────────── #

@app.post("/api/v1/policy/ingest", tags=["Policy Governance"])
async def policy_ingest(
    file: UploadFile = File(...),
    authority_level: str = Form("Global"),
    department: str = Form("General"),
    region: str = Form("Global"),
    version: str = Form("1.0"),
    db: Session = Depends(get_db)
):
    """
    Ingests an enterprise policy document, splits it into structured clauses,
    hashes the text to prevent duplicates, and maps relationship contradictions.
    """
    try:
        content_bytes = await file.read()
        content_text = content_bytes.decode("utf-8", errors="ignore")
        content_hash = hashlib.md5(content_text.strip().encode(), usedforsecurity=False).hexdigest()  # nosec B324

        # Deduplication validator
        existing = db.query(PolicyDocument).filter(PolicyDocument.content_hash == content_hash).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Document with identical content already ingested (ID: {existing.id})")

        # Create PolicyDocument
        doc = PolicyDocument(
            filename=file.filename,
            content_hash=content_hash,
            authority_level=authority_level,
            department=department,
            region=region,
            version=version
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Parse into hierarchical clauses
        chunks_data = PolicyParser.parse_document(content_text, doc.id)
        for c in chunks_data:
            db_chunk = PolicyChunk(
                document_id=doc.id,
                section_header=c["section_header"],
                clause_number=c["clause_number"],
                content=c["content"],
                authority_level=doc.authority_level,
                region=doc.region
            )
            db.add(db_chunk)
        db.commit()

        # Run contradiction & relationship engine
        GovernanceContradictionEngine.analyze_new_document(db, doc.id)

        return {
            "status": "success",
            "message": f"Successfully parsed and ingested policy document: {file.filename}",
            "document_id": doc.id,
            "clauses_extracted": len(chunks_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest policy: {str(e)}")


@app.get("/api/v1/policy/contradictions", tags=["Policy Governance"])
async def policy_contradictions(db: Session = Depends(get_db)):
    """Retrieves all active policy contradiction relationships with explainable rationales."""
    rels = db.query(PolicyRelationship).filter(PolicyRelationship.relationship_type == "CONTRADICTS").all()
    results = []
    for r in rels:
        src_chunk = db.query(PolicyChunk).filter(PolicyChunk.id == r.source_chunk_id).first()
        tgt_chunk = db.query(PolicyChunk).filter(PolicyChunk.id == r.target_chunk_id).first()
        
        if src_chunk and tgt_chunk:
            src_doc = db.query(PolicyDocument).filter(PolicyDocument.id == src_chunk.document_id).first()
            tgt_doc = db.query(PolicyDocument).filter(PolicyDocument.id == tgt_chunk.document_id).first()
            results.append({
                "id": r.id,
                "confidence": r.confidence,
                "rationale": r.rationale,
                "created_at": r.created_at,
                "source": {
                    "filename": src_doc.filename if src_doc else "Unknown",
                    "clause_number": src_chunk.clause_number,
                    "content": src_chunk.content,
                    "region": src_chunk.region,
                    "level": src_chunk.authority_level
                },
                "target": {
                    "filename": tgt_doc.filename if tgt_doc else "Unknown",
                    "clause_number": tgt_chunk.clause_number,
                    "content": tgt_chunk.content,
                    "region": tgt_chunk.region,
                    "level": tgt_chunk.authority_level
                }
            })
    return results


@app.get("/api/v1/policy/graph", tags=["Policy Governance"])
async def policy_graph(db: Session = Depends(get_db)):
    """Exposes all policy clauses and relationships as a node-edge graph for rendering."""
    nodes = []
    edges = []
    
    docs = db.query(PolicyDocument).all()
    for d in docs:
        nodes.append({
            "id": f"doc_{d.id}",
            "label": d.filename,
            "type": "document",
            "metadata": {"version": d.version, "region": d.region, "level": d.authority_level}
        })

    chunks = db.query(PolicyChunk).all()
    for c in chunks:
        nodes.append({
            "id": f"chunk_{c.id}",
            "label": f"Clause {c.clause_number}",
            "type": "clause",
            "metadata": {"header": c.section_header, "content": c.content[:150] + "..." if len(c.content) > 150 else c.content}
        })
        # Link clause to its parent document
        edges.append({
            "source": f"doc_{c.document_id}",
            "target": f"chunk_{c.id}",
            "type": "contains"
        })

    rels = db.query(PolicyRelationship).all()
    for r in rels:
        edges.append({
            "source": f"chunk_{r.source_chunk_id}",
            "target": f"chunk_{r.target_chunk_id}",
            "type": r.relationship_type,
            "metadata": {"confidence": r.confidence, "rationale": r.rationale}
        })

    return {"nodes": nodes, "edges": edges}


@app.get("/api/v1/policy/audit", tags=["Policy Governance"])
async def policy_audit(db: Session = Depends(get_db)):
    """Returns the immutable provenance timeline trail."""
    logs = db.query(AuditProvenanceLog).order_by(AuditProvenanceLog.timestamp.desc()).all()
    return logs


class RoutingRequest(BaseModel):
    department: str
    severity: str
    rationale: str

@app.post("/api/v1/policy/route", tags=["Policy Governance"])
async def policy_route(req: RoutingRequest, db: Session = Depends(get_db)):
    """Routes policy override alerts to the correct organizational authority."""
    target = GovernanceRouter.get_escalation_target(req.department, req.severity)
    
    # Log escalation to Audit memory
    log = AuditProvenanceLog(
        action="ESC_ROUTE",
        details=f"Escalated conflict to: {target}. Reason: {req.rationale}",
        actor="GOVERNANCE_ROUTER"
    )
    db.add(log)
    db.commit()
    
    return {
        "status": "routed",
        "authority_target": target,
        "timestamp": datetime.datetime.now().isoformat()
    }


@app.get("/api/v1/leo/hardware", tags=["Hardware"])
async def get_hardware_profile():
    """Returns the detected system hardware profile."""
    return global_leo_orchestrator.prod_router.profile

@app.get("/api/v1/leo/crystallization", tags=["Crystallization"])
async def get_crystallization_shortcuts():
    """Returns all compiled FSM lookup rules."""
    import sqlite3
    conn = sqlite3.connect("hyper_engine.db")
    c = conn.cursor()
    c.execute("SELECT shortcut_id, pattern_regex, response_template, hit_count, created_at FROM compiled_shortcuts")
    rows = c.fetchall()
    conn.close()
    return [
        {
            "shortcut_id": r[0],
            "pattern_regex": r[1],
            "response_template": r[2],
            "hit_count": r[3],
            "created_at": r[4]
        }
        for r in rows
    ]

@app.post("/api/v1/leo/crystallization/compile", tags=["Crystallization"])
async def trigger_crystallization():
    """Manually compiles frequent query traces into FSM lookup rules."""
    compiled_count = global_leo_orchestrator.prod_compiler.crystallize_frequent_patterns(min_hits=2)
    return {
        "status": "success",
        "compiled_rules_count": compiled_count,
        "message": f"Successfully compiled {compiled_count} FSM rules from trace history."
    }


# ── Health Check ─────────────────────────────────────────────────────────── #

@app.get("/health", tags=["Health"])
async def health_check():
    telemetry = global_leo_orchestrator.l15.get_metrics()
    return {
        "status": "ok",
        "system": global_leo_orchestrator.system_identity,
        "timestamp": time.time(),
        "avoidance_rate_pct": telemetry["avoidance_rate_pct"],
        "gpu_watts_saved": telemetry["gpu_watts_saved"],
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "LEO Semantic Compute Orchestration System — ACTIVE",
        "version": "2.0.0",
        "layers": 10,
        "principle": "Do not recompute what can be retrieved, cached, distilled, routed, approximated, predicted, or symbolically solved.",
        "docs": "/docs",
    }
