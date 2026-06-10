"""
tests/test_policy_system.py
Unit tests verifying ECOS Policy Relationship Intelligence System logic.
"""
from backend.core.policy_system import PolicyParser, SemanticIntelligenceMatcher, PolicyRelationshipClassifier
from backend.core.database import PolicyDocument, PolicyChunk

def test_hierarchical_policy_parsing():
    sample_policy = (
        "HUMAN RESOURCES LEAVE POLICY\n"
        "SECTION 1: ANNUAL LEAVE RULES\n"
        "1.1 All employees are allocated 25 days of annual leave.\n"
        "1.2 Leave must be approved by the regional line manager.\n"
        "SECTION 2: MATERNITY LEAVE RULES\n"
        "2.1 Maternity leave allocation is 12 weeks of paid leave."
    )
    chunks = PolicyParser.parse_document(sample_policy, document_id=1)
    
    assert len(chunks) == 3
    assert chunks[0]["section_header"] == "SECTION 1: ANNUAL LEAVE RULES"
    assert chunks[0]["clause_number"] == "1.1"
    assert "25 days" in chunks[0]["content"]
    assert chunks[2]["section_header"] == "SECTION 2: MATERNITY LEAVE RULES"
    assert chunks[2]["clause_number"] == "2.1"


def test_semantic_similarity():
    text_a = "All employees are entitled to twenty five days of paid annual leave."
    text_b = "Employees shall get 25 days of paid annual leave every calendar year."
    text_c = "Maternity leave is capped at twelve weeks of paid allocation."
    
    sim_ab = SemanticIntelligenceMatcher.calculate_similarity(text_a, text_b)
    sim_ac = SemanticIntelligenceMatcher.calculate_similarity(text_a, text_c)
    
    assert sim_ab > 0.4
    assert sim_ab > sim_ac


def test_policy_contradiction_detection():
    # Setup mock data
    doc_a = PolicyDocument(id=1, filename="Global_Leave_Policy.txt", region="Global", version="1.0")
    doc_b = PolicyDocument(id=2, filename="Global_Leave_Policy.txt", region="Global", version="2.0")
    
    chunk_a = PolicyChunk(id=101, clause_number="1.1", content="Employees are allowed to carry over 5 days of unused leave.")
    chunk_b = PolicyChunk(id=102, clause_number="1.1", content="Employees are carry over 10 days of unused leave.")
    
    # 1. Test version supersedes
    rel, conf, rationale = PolicyRelationshipClassifier.classify_relationship(chunk_a, chunk_b, doc_a, doc_b)
    assert rel == "SUPERSEDES"
    assert conf == 1.0
    
    # 2. Test semantic command contradiction
    doc_c = PolicyDocument(id=3, filename="Office_Policy.txt", region="Global", version="1.0")
    doc_d = PolicyDocument(id=4, filename="Office_Policy.txt", region="Global", version="1.0")
    chunk_c = PolicyChunk(id=103, clause_number="2.1", content="Working from home is strictly allowed for everyone.")
    chunk_d = PolicyChunk(id=104, clause_number="2.2", content="Working from home is forbidden for everyone.")
    
    rel_contra, conf_contra, rationale_contra = PolicyRelationshipClassifier.classify_relationship(chunk_c, chunk_d, doc_c, doc_d)
    assert rel_contra == "CONTRADICTS"
    assert conf_contra == 0.9
    assert "forbidden" in rationale_contra or "allowed" in rationale_contra

    # 3. Test numeric conflict
    chunk_e = PolicyChunk(id=105, clause_number="3.1", content="Unused leave is capped at 5 days maximum.")
    chunk_f = PolicyChunk(id=106, clause_number="3.2", content="Unused leave is capped at 10 days maximum.")
    
    rel_num, conf_num, rationale_num = PolicyRelationshipClassifier.classify_relationship(chunk_e, chunk_f, doc_c, doc_d)
    assert rel_num == "CONTRADICTS"
    assert "numeric" in rationale_num.lower()


def test_regional_override_exception():
    doc_global = PolicyDocument(id=1, filename="Global_SOP.txt", region="Global", version="1.0")
    doc_regional = PolicyDocument(id=2, filename="EU_SOP.txt", region="EU", version="1.0")
    
    chunk_global = PolicyChunk(id=101, clause_number="4.1", content="The standard probation period is 6 months global limit.")
    chunk_regional = PolicyChunk(id=102, clause_number="4.1", content="In Europe, probation period overrides to 3 months local limit.")
    
    rel, conf, rationale = PolicyRelationshipClassifier.classify_relationship(chunk_global, chunk_regional, doc_global, doc_regional)
    assert rel == "REGION_EXCEPTION"
    assert conf == 0.95
    assert "overrides" in rationale
