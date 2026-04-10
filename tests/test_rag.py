import pytest
import asyncio
from backend.intelligence.rag import RAGEngine

@pytest.mark.asyncio
async def test_rag_isolation():
    """Test that RAG correctly isolates documents by tenant_id."""
    rag = RAGEngine(persist_dir="test_rag_data")
    
    # Add docs for different tenants
    await rag.add_documents(["Secret for Tenant A"], tenant_id="tenant_a")
    await rag.add_documents(["Secret for Tenant B"], tenant_id="tenant_b")
    
    # Retrieve as Tenant A
    results_a = rag.retrieve("Secret", tenant_id="tenant_a", k=1)
    assert len(results_a) == 1
    assert "Tenant A" in results_a[0]["content"]
    assert "Tenant B" not in results_a[0]["content"]
    
    # Clean up test data
    import shutil
    shutil.rmtree("test_rag_data", ignore_errors=True)
