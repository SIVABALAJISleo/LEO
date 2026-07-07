"""
tests/test_crystallizer.py
Unit tests for the Layer 4 Semantic Crystallizer Cache.
"""

import os
import pytest
from backend.crystallization.crystallizer import SemanticCrystallizer


@pytest.fixture
def temp_db():
    db_name = "test_cryst_temp.db"
    if os.path.exists(db_name):
        os.remove(db_name)
    yield db_name
    if os.path.exists(db_name):
        os.remove(db_name)


def test_crystallizer_flow(temp_db):
    crystallizer = SemanticCrystallizer(db_path=temp_db)

    # 1. Initially it should return None since cache is empty
    match = crystallizer.match_shortcut("What is LEO AI?")
    assert match is None

    # 2. Record a trace
    crystallizer.record_trace(
        trace_id="trace_123",
        query="What is LEO AI?",
        response="LEO AI is an on-device optimization fabric engine.",
        w_class="general"
    )

    # 3. Match the recorded query (exact match)
    match = crystallizer.match_shortcut("What is LEO AI?")
    assert match is not None
    assert match["shortcut_id"] == "trace_123"
    assert "optimization fabric" in match["response"]
    assert match["similarity"] >= 0.99

    # 4. Match semantic similarity (fuzzy match)
    match_fuzzy = crystallizer.match_shortcut("Tell me what LEO AI is")
    assert match_fuzzy is not None
    assert match_fuzzy["shortcut_id"] == "trace_123"

    # 5. Template rephrasing check
    match_greeting = crystallizer.match_shortcut("Hello, what is LEO AI?")
    assert match_greeting is not None
    assert match_greeting["response"].startswith("Hello! Here is your crystallized response:")

    # 6. Invalidation check
    crystallizer.invalidate_trace("trace_123")
    match_after = crystallizer.match_shortcut("What is LEO AI?")
    assert match_after is None
