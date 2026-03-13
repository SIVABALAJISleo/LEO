import py
import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.query import RagQueryEngine
from experts.router import MoERouter

def test_rag_query():
    engine = RagQueryEngine()
    # Add dummy data
    engine.index.add(engine.embedder.get_embeddings("Unit testing is good"), [{"text": "Unit testing is good"}])
    res = engine.query("testing")
    assert "Unit testing is good" in res['context']
    print("RAG Test Passed")

def test_moe_routing():
    router = MoERouter()
    res = router.route("def test(): pass")
    assert res['chosen_expert'] == "code"
    
    res = router.route("calculate sum of 1 and 2")
    assert res['chosen_expert'] == "math"
    print("MoE Test Passed")

if __name__ == "__main__":
    test_rag_query()
    test_moe_routing()
