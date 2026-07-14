"""
tests/test_phase3.py
Phase 3 Verification: Intelligence & Reasoning subsystems.
"""
import logging
import sys
import os
import numpy as np

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.memory.hierarchical_memory import HierarchicalMemory
from backend.knowledge.knowledge_graph import KnowledgeGraph
from backend.intelligence.hybrid_intelligence import HybridIntelligenceEngine
from backend.intelligence.self_verification import SelfVerificationEngine


def test_hierarchical_memory():
    logger.info("[Test] 5. Hierarchical Memory System")
    mem = HierarchicalMemory(db_path=":memory:")  # SQLite in-memory for tests

    # Working Memory
    mem.working.set("last_query", "What is Python?")
    assert mem.working.get("last_query") == "What is Python?"

    # Working Memory capacity eviction
    for i in range(35):
        mem.working.set(f"key_{i}", i)
    assert len(mem.working.store) <= 32, "Working memory exceeded capacity"

    # Episodic Memory
    mem.record_turn("user", "Hello LEO!")
    mem.record_turn("assistant", "Hello! How can I help?")
    history = mem.get_recent_context(limit=5)
    assert len(history) == 2
    assert history[-1]["role"] == "assistant"

    # Semantic Memory
    v1 = np.array([1.0, 0.0, 0.5])
    mem.semantic.store("Python is a programming language.", v1, {"source": "wiki"})
    results = mem.semantic.query(np.array([0.9, 0.1, 0.4]), top_k=1)
    assert len(results) == 1
    assert "Python" in results[0]["text"]

    logger.info("✅ Hierarchical Memory verified.")


def test_knowledge_graph():
    logger.info("\n[Test] 6. Knowledge Graph Engine")
    kg = KnowledgeGraph()

    # Add entities
    kg.add_entity("e1", "Python", "LANGUAGE", {"year": 1991})
    kg.add_entity("e2", "Guido van Rossum", "PERSON")
    kg.add_entity("e3", "Google", "ORGANIZATION")
    kg.add_entity("e4", "TensorFlow", "LIBRARY")

    # Add relations
    kg.add_relation("e2", "e1", "CREATED")
    kg.add_relation("e3", "e4", "DEVELOPED")
    kg.add_relation("e4", "e1", "WRITTEN_IN")

    # O(1) entity lookup by label
    entity = kg.get_entity_by_label("python")
    assert entity is not None and entity.entity_id == "e1"

    # Neighbor traversal
    neighbors = kg.get_neighbors("e3")
    assert any(n.entity_id == "e4" for n, _ in neighbors)

    # BFS path: Google -> Python (via TensorFlow -> Python)
    path = kg.bfs_path("e3", "e1", max_hops=4)
    assert path is not None, "BFS path not found"
    assert path[0] == "e3" and path[-1] == "e1"
    logger.info(f"   BFS path: {' -> '.join(kg.entities[eid].label for eid in path)}")

    # Fact inference
    facts = kg.infer_relationships("e2")
    assert any(f["predicate"] == "CREATED" for f in facts)

    stats = kg.stats()
    logger.info(f"   Graph stats: {stats}")
    assert stats["entity_count"] == 4
    logger.info("✅ Knowledge Graph verified.")


def test_hybrid_intelligence():
    logger.info("\n[Test] 7. Hybrid Intelligence Engine")
    engine = HybridIntelligenceEngine()

    # Prime detection
    r1 = engine.solve("is 17 prime?")
    assert r1 and "prime" in r1.lower(), f"Prime rule failed: {r1}"
    logger.info(f"   Prime check: {r1}")

    r2 = engine.solve("is 18 prime")
    assert r2 and "not a prime" in r2.lower(), f"Non-prime rule failed: {r2}"

    # Fibonacci
    r3 = engine.solve("fibonacci of 10")
    assert "55" in r3, f"Fibonacci rule failed: {r3}"
    logger.info(f"   Fibonacci: {r3}")

    # GCD
    r4 = engine.solve("gcd of 48 and 18")
    assert "6" in r4, f"GCD rule failed: {r4}"
    logger.info(f"   GCD: {r4}")

    # Square root
    r5 = engine.solve("square root of 144")
    assert "12" in r5, f"Sqrt rule failed: {r5}"
    logger.info(f"   Sqrt: {r5}")

    # No match → None
    r6 = engine.solve("write me an essay about Shakespeare")
    assert r6 is None, "Should return None for unmatched query"

    logger.info("✅ Hybrid Intelligence Engine verified.")


def test_self_verification():
    logger.info("\n[Test] 19. Self-Verification Engine")
    verifier = SelfVerificationEngine(min_confidence=0.15)

    # High confidence: answer is well-supported by sources
    sources = ["Python is a high-level programming language created by Guido van Rossum in 1991."]
    good_answer = "Python is a programming language created by Guido."
    report = verifier.verify(good_answer, sources)
    logger.info(f"   Good answer confidence: {report['confidence_score']}")
    assert report["confidence_score"] > 0.5, "Expected high confidence"
    assert report["verification_passed"], "Expected to pass"

    # Low confidence: answer is unrelated to sources
    bad_answer = "The Eiffel Tower stands at 330 metres. Studies show it attracts 7 million visitors."
    report2 = verifier.verify(bad_answer, sources)
    logger.info(f"   Bad answer confidence: {report2['confidence_score']}, flags: {report2['flags']}")
    assert not report2["verification_passed"], "Expected to fail verification"

    logger.info("✅ Self-Verification Engine verified.")


if __name__ == "__main__":
    test_hierarchical_memory()
    test_knowledge_graph()
    test_hybrid_intelligence()
    test_self_verification()
    logger.info("\n🚀 Phase 3 Intelligence & Reasoning: FULLY FUNCTIONAL")
