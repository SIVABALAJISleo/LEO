import hashlib
import datetime
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db, PolicyDocument, PolicyChunk, PolicyRelationship, AuditProvenanceLog
from backend.core.policy_system import PolicyParser, GovernanceContradictionEngine, GovernanceRouter
from pydantic import BaseModel

from backend.security.rbac import PermissionChecker

router = APIRouter()

@router.post("/api/v1/policy/ingest", tags=["Policy Governance"])
async def policy_ingest(
    file: UploadFile = File(...),
    authority_level: str = Form("Global"),
    department: str = Form("General"),
    region: str = Form("Global"),
    version: str = Form("1.0"),
    db: Session = Depends(get_db),
    token: dict = Depends(PermissionChecker("upload"))
):
    try:
        content_bytes = await file.read()
        content_text = content_bytes.decode("utf-8", errors="ignore")
        content_hash = hashlib.md5(content_text.strip().encode(), usedforsecurity=False).hexdigest()

        existing = db.query(PolicyDocument).filter(PolicyDocument.content_hash == content_hash).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Document with identical content already ingested (ID: {existing.id})")

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

@router.get("/api/v1/policy/contradictions", tags=["Policy Governance"])
async def policy_contradictions(db: Session = Depends(get_db), token: dict = Depends(PermissionChecker("orchestrate"))):
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

@router.get("/api/v1/policy/graph", tags=["Policy Governance"])
async def policy_graph(db: Session = Depends(get_db), token: dict = Depends(PermissionChecker("orchestrate"))):
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

@router.get("/api/v1/policy/audit", tags=["Policy Governance"])
async def policy_audit(db: Session = Depends(get_db), token: dict = Depends(PermissionChecker("admin"))):
    logs = db.query(AuditProvenanceLog).order_by(AuditProvenanceLog.timestamp.desc()).all()
    return logs

class RoutingRequest(BaseModel):
    department: str
    severity: str
    rationale: str

@router.post("/api/v1/policy/route", tags=["Policy Governance"])
async def policy_route(req: RoutingRequest, db: Session = Depends(get_db), token: dict = Depends(PermissionChecker("orchestrate"))):
    target = GovernanceRouter.get_escalation_target(req.department, req.severity)
    
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
