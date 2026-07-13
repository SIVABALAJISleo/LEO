"""
tests/test_domain_experts.py
Verifies correct execution of the 10 specialized domain experts and the TF-IDF MoE router.
"""

import pytest
from experts.router import MoERouter
from experts.domain_experts import (
    ReasoningExpert,
    MathematicsExpert,
    CodingExpert,
    CybersecurityExpert,
    CreativeWritingExpert,
    SummarizationExpert,
    TranslationExpert,
    ConversationExpert,
    PlanningExpert,
    DocumentUnderstandingExpert
)

def test_reasoning_expert():
    expert = ReasoningExpert()
    res = expert.run("If A, then B. Know that A.")
    assert "deduced 'b'" in res.lower()
    assert "conclusion" in res.lower()

def test_math_expert():
    expert = MathematicsExpert()
    res = expert.run("Compute the values: 5 + 10 - 2 * 3")
    assert "9.0" in res

    # Division by zero safety
    res_zero = expert.run("10 / 0")
    assert "division by zero" in res_zero.lower()

def test_coding_expert():
    expert = CodingExpert()
    res = expert.run("def compute_data(): for i in range(100): val += i")
    assert "loop" in res.lower()
    assert "numpy" in res.lower() or "simd" in res.lower()

def test_cybersecurity_expert():
    expert = CybersecurityExpert()
    res_safe = expert.run("Select the best candidate from the table.")
    assert "no malicious patterns" in res_safe.lower()

    res_vuln = expert.run("SELECT * FROM users UNION SELECT null, username, password")
    assert "sql injection" in res_vuln.lower()

def test_creative_expert():
    expert = CreativeWritingExpert()
    res = expert.run("Write a sad narrative story.")
    assert "melancholic" in res.lower()

def test_summarization_expert():
    expert = SummarizationExpert()
    text = "LEO AI is a high performance execution fabric. It optimizes memory allocations. It uses custom SIMD kernels. This completes the summary."
    res = expert.run(text)
    assert "summary" in res.lower()

def test_translation_expert():
    expert = TranslationExpert()
    res_te = expert.run("hello world in Telugu")
    assert "హలో" in res_te
    res_kn = expert.run("hello world in Kannada")
    assert "ಹಲೋ" in res_kn

def test_conversation_expert():
    expert = ConversationExpert()
    res = expert.run("Hello there LEO AI!")
    assert "greeting intent" in res.lower()

def test_planning_expert():
    expert = PlanningExpert()
    # Task B depends on A
    res = expert.run("TaskB depends on TaskA")
    assert "taska -> taskb" in res.lower()

def test_document_expert():
    expert = DocumentUnderstandingExpert()
    res = expert.run("Paragraph one content.\nParagraph two content.")
    assert "paragraph 1" in res.lower()

def test_moe_router_routing():
    router = MoERouter()
    
    # 1. Coding match
    res_code = router.route("def optimize_memory(): return None")
    assert res_code["chosen_expert"] == "coding"
    
    # 2. Math match
    res_math = router.route("calculate the sum: 15 + 45")
    assert res_math["chosen_expert"] == "mathematics"
    
    # 3. Fallback check (low similarity routing)
    res_fallback = router.route("random request string that does not match any keyword sequence")
    assert res_fallback["chosen_expert"] == "conversation"
