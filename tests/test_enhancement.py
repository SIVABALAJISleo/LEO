import pytest
from backend.enhancement.enhancement_pipeline import global_enhancement_pipeline
from backend.enhancement.quality_scorer import QualityScorer
from backend.enhancement.confidence_estimator import ConfidenceEstimator

def test_quality_scorer():
    scorer = QualityScorer()
    
    # Needs to be > 0.5 to trigger enhancement
    good_text = "This is a detailed explanation. It covers the core concepts clearly. For example, it ensures high reliability."
    assert scorer.score(good_text) > 0.5
    
    weak_text = "i don't know error"
    assert scorer.score(weak_text) < 0.2
    
def test_confidence_estimator():
    estimator = ConfidenceEstimator()
    
    # Needs to be > 0.6 to trigger enhancement
    confident = "It specifically refers to the process. This always works for the system."
    assert estimator.estimate(confident) > 0.6
    
    uncertain = "It might be possible, but I am not sure and it is unknown."
    assert estimator.estimate(uncertain) < 0.5
    
def test_enhancement_pipeline_success():
    raw_answer = "RAG retrieval output system architecture. It refers to the pipeline layer."
    query = "What is the RAG architecture?"
    
    final, status = global_enhancement_pipeline.run(raw_answer, query, ["Extra RAG doc context 1"], "definition")
    
    # Format and expansion should have applied
    assert status == "enhancement_success"
    assert "architecture" in final.lower()
    assert "•" in final or "**" in final or "Context" in final  # Proves templates/expander hit
    
def test_enhancement_pipeline_fallback():
    raw_answer = "error unknown"
    query = "explain X"
    
    final, status = global_enhancement_pipeline.run(raw_answer, query)
    
    assert status == "fallback_required"
    assert "error unknown" in final
