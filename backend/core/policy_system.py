"""
backend/core/policy_system.py
ECOS: Enterprise Policy Relationship Intelligence & Semantic Audit Memory Engine
"""
import re
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from backend.core.database import PolicyDocument, PolicyChunk, PolicyRelationship, AuditProvenanceLog

class PolicyParser:
    """Section-aware chunking parser that preserves headings, clauses, and structure."""
    
    @staticmethod
    def parse_document(text: str, document_id: int) -> List[Dict[str, Any]]:
        lines = text.split("\n")
        chunks = []
        current_section = "General Provision"
        current_clause = "0.0"
        current_text = []

        clause_regex = re.compile(
            r"^(?:section|clause|article|part|policy)?\s*(\d+(?:\.\d+)*[a-z]?)\b", 
            re.IGNORECASE
        )

        for line in lines:
            line_strip = line.strip()
            if not line_strip:
                continue

            # Header detection (all caps, short, or ends with colon)
            if len(line_strip) < 60 and (line_strip.isupper() or line_strip.endswith(":")):
                # Save previous chunk if exists
                if current_text:
                    chunks.append({
                        "document_id": document_id,
                        "section_header": current_section,
                        "clause_number": current_clause,
                        "content": " ".join(current_text)
                    })
                    current_text = []
                current_section = line_strip
                continue

            # Clause number detection
            m = clause_regex.match(line_strip)
            if m:
                if current_text:
                    chunks.append({
                        "document_id": document_id,
                        "section_header": current_section,
                        "clause_number": current_clause,
                        "content": " ".join(current_text)
                    })
                    current_text = []
                current_clause = m.group(1)
                current_text.append(line_strip)
            else:
                current_text.append(line_strip)

        if current_text:
            chunks.append({
                "document_id": document_id,
                "section_header": current_section,
                "clause_number": current_clause,
                "content": " ".join(current_text)
            })

        return chunks


class SemanticIntelligenceMatcher:
    """Lightweight CPU-first Tf-Idf and Cosine similarity matcher for policy text."""
    
    @staticmethod
    def _get_bag_of_words(text: str) -> Dict[str, int]:
        words = re.findall(r"\w+", text.lower())
        bag = {}
        for w in words:
            if len(w) > 2:  # Ignore very short stop words
                bag[w] = bag.get(w, 0) + 1
        return bag

    @classmethod
    def calculate_similarity(cls, text_a: str, text_b: str) -> float:
        bag_a = cls._get_bag_of_words(text_a)
        bag_b = cls._get_bag_of_words(text_b)
        
        all_words = set(bag_a.keys()).union(set(bag_b.keys()))
        dot_product = sum(bag_a.get(w, 0) * bag_b.get(w, 0) for w in all_words)
        
        norm_a = math.sqrt(sum(v*v for v in bag_a.values()))
        norm_b = math.sqrt(sum(v*v for v in bag_b.values()))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)


import math # Ensure math import is present for similarity function

class PolicyRelationshipClassifier:
    """Classifies relationships between policy chunks using symbolic and semantic heuristics."""

    CONTRADICTION_KEYWORDS = [
        ("must", "must not"),
        ("shall", "shall not"),
        ("required", "prohibited"),
        ("allowed", "forbidden"),
        ("mandatory", "optional"),
        ("limit", "no limit"),
        ("approve", "reject")
    ]

    @classmethod
    def classify_relationship(
        cls, 
        chunk_a: PolicyChunk, 
        chunk_b: PolicyChunk,
        doc_a: PolicyDocument,
        doc_b: PolicyDocument
    ) -> Tuple[Optional[str], float, str]:
        """
        Determines the semantic relationship between two policy chunks.
        Returns: (RelationshipType, Confidence, Rationale)
        """
        content_a = chunk_a.content.lower()
        content_b = chunk_b.content.lower()

        # Calculate base concept overlap
        similarity = SemanticIntelligenceMatcher.calculate_similarity(content_a, content_b)
        if similarity < 0.25:
            return None, 0.0, ""

        # 1. Check for explicit version SUPERSEDES
        if doc_a.filename == doc_b.filename and doc_a.id != doc_b.id:
            try:
                v_a = float(re.findall(r"\d+\.?\d*", doc_a.version or "1.0")[0])
                v_b = float(re.findall(r"\d+\.?\d*", doc_b.version or "1.0")[0])
                if v_b > v_a:
                    return (
                        "SUPERSEDES", 
                        1.0, 
                        f"Policy document version {doc_b.version} is newer than version {doc_a.version}."
                    )
            except Exception:
                if doc_b.created_at > doc_a.created_at:
                    return (
                        "SUPERSEDES", 
                        0.9, 
                        f"Document {doc_b.filename} ingested on {doc_b.created_at} replaces {doc_a.filename}."
                    )

        # 2. Check for Scope Exceptions (Regional Override)
        if doc_a.region != doc_b.region:
            # Regional overriding general rules
            if doc_a.region == "Global" and doc_b.region != "Global":
                return (
                    "REGION_EXCEPTION",
                    0.95,
                    f"Clause {chunk_b.clause_number} in region {doc_b.region} overrides general global policy {chunk_a.clause_number}."
                )
            if doc_b.region == "Global" and doc_a.region != "Global":
                return (
                    "REGION_EXCEPTION",
                    0.95,
                    f"Clause {chunk_a.clause_number} in region {doc_a.region} overrides general global policy {chunk_b.clause_number}."
                )

        # 3. Check for contradictions (Opposing commands or mismatch limits)
        for term_a, term_b in cls.CONTRADICTION_KEYWORDS:
            if (term_a in content_a and term_b in content_b) or (term_b in content_a and term_a in content_b):
                return (
                    "CONTRADICTS",
                    0.9,
                    f"Semantic contradiction detected between command '{term_a}' in one clause and '{term_b}' in the other regarding similar concepts."
                )

        # Check numeric constraint conflicts (e.g. '30 days' vs '20 days')
        nums_a = re.findall(r"\b\d+\b", content_a)
        nums_b = re.findall(r"\b\d+\b", content_b)
        if nums_a and nums_b and similarity > 0.5:
            # Check if numbers mismatch while contexts are highly similar
            if set(nums_a) != set(nums_b):
                return (
                    "CONTRADICTS",
                    0.85,
                    f"Conflicting numeric constraints detected (Values in A: {nums_a} vs. Values in B: {nums_b}) on similar conceptual context."
                )

        # 4. Check for DUPLICATES / References
        if similarity > 0.95:
            return "DUPLICATES", 0.98, "The clause contents are semantically identical."
            
        if "depend" in content_a or "require" in content_a:
            if chunk_b.clause_number in content_a or doc_b.filename.lower() in content_a:
                return "DEPENDS_ON", 0.9, f"Clause {chunk_a.clause_number} explicitly defines a dependency on {chunk_b.clause_number}."

        if chunk_b.clause_number in content_a:
            return "REFERENCES", 0.85, f"Clause {chunk_a.clause_number} references clause {chunk_b.clause_number}."

        # Default fallback context relation
        if similarity > 0.45:
            return "SUPPORTS", round(similarity, 2), "The clauses share high conceptual correlation."

        return None, 0.0, ""


class GovernanceContradictionEngine:
    """Core coordinator running the relationship verification cascade on database session."""
    
    @staticmethod
    def analyze_new_document(db: Session, doc_id: int):
        """Compares chunks of a newly ingested policy document against all existing policy chunks."""
        new_doc = db.query(PolicyDocument).filter(PolicyDocument.id == doc_id).first()
        if not new_doc:
            return

        new_chunks = db.query(PolicyChunk).filter(PolicyChunk.document_id == doc_id).all()
        all_other_docs = db.query(PolicyDocument).filter(PolicyDocument.id != doc_id).all()

        relationships_found = 0
        audit_details = []

        for other_doc in all_other_docs:
            other_chunks = db.query(PolicyChunk).filter(PolicyChunk.document_id == other_doc.id).all()
            for n_chunk in new_chunks:
                for o_chunk in other_chunks:
                    rel_type, confidence, rationale = PolicyRelationshipClassifier.classify_relationship(
                        o_chunk, n_chunk, other_doc, new_doc
                    )
                    
                    if rel_type:
                        # Log relationship in DB
                        db_rel = PolicyRelationship(
                            source_chunk_id=o_chunk.id,
                            target_chunk_id=n_chunk.id,
                            relationship_type=rel_type,
                            confidence=confidence,
                            rationale=rationale
                        )
                        db.add(db_rel)
                        relationships_found += 1
                        
                        if rel_type == "CONTRADICTS":
                            audit_details.append(
                                f"Contradiction found between {other_doc.filename} ({o_chunk.clause_number}) "
                                f"and {new_doc.filename} ({n_chunk.clause_number}). Reason: {rationale}"
                            )

        # Commit relationships
        db.commit()

        # Log to Audit Memory
        action_log = AuditProvenanceLog(
            action="INGEST",
            document_id=doc_id,
            details=f"Ingested {new_doc.filename}. Analyzed {len(new_chunks)} clauses. "
                    f"Identified {relationships_found} relationships. "
                    f"Contradictions flagged: {len(audit_details)}.",
            actor="SYSTEM_AUTO_INGEST"
        )
        db.add(action_log)
        db.commit()


class GovernanceRouter:
    """Decides escalation routing paths based on conflict details and departments."""
    
    DEPARTMENTS_ROUTING = {
        "hr": "HR Governance Officer (hr-esc@enterprise.local)",
        "legal": "Legal Compliance Council (legal-audit@enterprise.local)",
        "security": "Chief Information Security Officer (ciso-alert@enterprise.local)",
        "finance": "Finance Controller Team (finance-audit@enterprise.local)"
    }

    @classmethod
    def get_escalation_target(cls, department: str, severity: str) -> str:
        dept = department.lower().strip()
        target = cls.DEPARTMENTS_ROUTING.get(dept, "Central Policy Governance Group (policy-esc@enterprise.local)")
        return f"{target} [Priority: {severity.upper()}]"
