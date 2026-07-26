from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    """Test standard health monitor endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_root():
    """Test root entry point."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Universal" in response.json()["message"]

def test_mock_token_rejected_in_production():
    """Verify mock token auth is rejected when APP_ENV is production."""
    import os
    old_env = os.environ.get("APP_ENV")
    os.environ["APP_ENV"] = "production"
    
    try:
        response = client.get("/api/v1/devops/status", headers={"Authorization": "Bearer token-admin"})
        assert response.status_code == 401
    finally:
        if old_env is not None:
            os.environ["APP_ENV"] = old_env
        else:
            del os.environ["APP_ENV"]

def test_custom_auth_flow():
    """Verify backend-owned signup and login flow."""
    import uuid
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "SuperPassword123!"
    
    # 1. Signup
    signup_resp = client.post("/api/v1/auth/signup", json={"email": email, "password": password})
    assert signup_resp.status_code == 200
    signup_json = signup_resp.json()
    assert "token" in signup_json
    assert signup_json["user"]["email"] == email
    assert "leo.jwt" in signup_resp.cookies
    
    # 2. Login
    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login_resp.status_code == 200
    login_json = login_resp.json()
    assert "token" in login_json
    assert login_json["user"]["email"] == email
    assert "leo.jwt" in login_resp.cookies
    
    # 3. Login with wrong password
    wrong_resp = client.post("/api/v1/auth/login", json={"email": email, "password": "wrong_password"})
    assert wrong_resp.status_code == 401

def test_database_cascade_delete():
    """Verify referential integrity and cascade delete under SQLite."""
    from backend.core.database import SessionLocal, PolicyDocument, PolicyChunk
    
    db = SessionLocal()
    try:
        # Create parent doc
        doc = PolicyDocument(
            filename="test_policy.txt",
            content_hash="hash_test_12345",
            authority_level="Global",
            department="QA",
            region="US",
            version="1.0"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        # Create child chunk
        chunk = PolicyChunk(
            document_id=doc.id,
            section_header="Introduction",
            clause_number="1.1",
            content="This is a test policy clause.",
            authority_level="Global",
            region="US"
        )
        db.add(chunk)
        db.commit()
        db.refresh(chunk)
        
        # Verify chunk exists
        chunk_id = chunk.id
        assert db.query(PolicyChunk).filter(PolicyChunk.id == chunk_id).first() is not None
        
        # Delete parent doc
        db.delete(doc)
        db.commit()
        
        # Verify child chunk was automatically cascading-deleted
        child = db.query(PolicyChunk).filter(PolicyChunk.id == chunk_id).first()
        assert child is None
    finally:
        db.close()

def test_stripe_webhook_verification():
    """Verify that Stripe signature verification behaves correctly."""
    import stripe
    import os
    import time
    
    os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_secret"
    
    # 1. Missing header
    resp = client.post("/api/v1/billing/webhook", content="{}", headers={})
    assert resp.status_code == 400
    
    # 2. Malformed signature
    resp = client.post("/api/v1/billing/webhook", content="{}", headers={"stripe-signature": "invalid_signature"})
    assert resp.status_code in (400, 401)
    
    # 3. Mismatched signature
    resp = client.post("/api/v1/billing/webhook", content="{}", headers={"stripe-signature": "t=123,v1=abc"})
    assert resp.status_code == 401
    
    # 4. Valid signature
    payload = '{"id": "evt_test"}'
    timestamp = int(time.time())
    payload_to_sign = f"{timestamp}.{payload}"
    scheme = stripe.WebhookSignature._compute_signature(payload_to_sign, "whsec_test_secret")
    sig_header = f"t={timestamp},v1={scheme}"
    
    resp = client.post("/api/v1/billing/webhook", content=payload, headers={"stripe-signature": sig_header})
    assert resp.status_code == 200
    assert resp.json()["status"] == "verified"
