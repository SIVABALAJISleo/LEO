"""
tests/test_document_knowledge.py
Verifies multi-format document text extraction, Jaccard duplicate detection, and citation indexing.
"""

import os
import zipfile
import pytest
from backend.intelligence.document_processor import DocumentProcessor
from backend.intelligence.knowledge_engine import KnowledgeEngine

@pytest.fixture
def temp_files(tmp_path):
    # Setup multiple test files in a temp directory
    txt_file = tmp_path / "doc.txt"
    txt_file.write_text("LEO AI is a high performance execution system.", encoding="utf-8")
    
    md_file = tmp_path / "doc.md"
    md_file.write_text("# LEO AI\n\nOptimizes CPU memory allocations.", encoding="utf-8")
    
    csv_file = tmp_path / "doc.csv"
    csv_file.write_text("name,value\nLEO,100\nIntel,200", encoding="utf-8")
    
    return {
        "txt": str(txt_file),
        "md": str(md_file),
        "csv": str(csv_file)
    }

def test_document_processor_parsing(temp_files):
    processor = DocumentProcessor()
    
    # 1. TXT parse
    text_txt = processor.extract_text(temp_files["txt"])
    assert "LEO AI is a high performance" in text_txt
    
    # 2. Markdown parse
    text_md = processor.extract_text(temp_files["md"])
    assert "LEO" in text_md
    assert "#" not in text_md  # should strip header syntax
    
    # 3. CSV parse
    text_csv = processor.extract_text(temp_files["csv"])
    assert "LEO | 100" in text_csv

def test_knowledge_engine_indexing_and_search():
    engine = KnowledgeEngine()
    
    # Add documents
    doc1 = "LEO AI implements cache-aware thread scheduling for Intel Core CPUs."
    doc2 = "LEO AI implements cache-aware thread scheduling for Intel Core CPUs." # Duplicate
    doc3 = "Distributed mesh framework handles task balancing across peer nodes."
    
    added1 = engine.add_document("doc_intel.txt", doc1)
    added2 = engine.add_document("doc_duplicate.txt", doc2)
    added3 = engine.add_document("doc_mesh.txt", doc3)
    
    assert added1 > 0
    assert added2 == 0  # Duplicate should be blocked by Jaccard similarity threshold!
    assert added3 > 0
    
    # Search check
    citations = engine.search("Intel thread scheduling", top_k=2)
    assert len(citations) > 0
    assert citations[0]["source"] == "doc_intel.txt"
    assert "[Source:" in citations[0]["citation"]
    
    # Relationship Graph check
    rel_map = engine.graph.get_relationship_map()
    # Relationship extraction: "LEO AI implements cache-aware thread scheduling"
    # Should detect "Leo Ai" -> "implements" -> "Cache-Aware Thread Scheduling" (titled)
    assert "Leo Ai" in rel_map


def test_rag_evaluator():
    from backend.layers.v_infinity_orchestrator import VInfinityOrchestrator
    from backend.intelligence.rag_evaluator import RAGEvaluator
    
    orchestrator = VInfinityOrchestrator()
    evaluator = RAGEvaluator()
    results = evaluator.run_eval_suite(orchestrator)
    
    assert results["total_cases_run"] == 3
    assert "metrics" in results
    assert results["metrics"]["answer_correctness_rate"] > 0.0
    assert results["metrics"]["average_groundedness"] >= 0.0
