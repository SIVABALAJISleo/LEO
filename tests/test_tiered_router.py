"""
tests/test_tiered_router.py
Unit tests for the TieredIntelligenceRouter and complexity classifier.
"""

import pytest
import asyncio
from core_ai.tiered_router import classify_complexity, InferenceTier, TieredIntelligenceRouter


# ── classify_complexity ───────────────────────────────────────────────────────

def test_fast_tier_greeting():
    assert classify_complexity("Hello!") == InferenceTier.FAST

def test_fast_tier_translate():
    assert classify_complexity("Translate this to French") == InferenceTier.FAST

def test_smart_tier_medium_question():
    result = classify_complexity("What is the difference between TCP and UDP?")
    assert result == InferenceTier.SMART

def test_deep_tier_keyword_analyze():
    result = classify_complexity("Analyze the architecture of the LEO AI system end to end.")
    assert result == InferenceTier.DEEP

def test_deep_tier_long_prompt():
    long_prompt = "word " * 90  # > 80 words triggers DEEP
    assert classify_complexity(long_prompt) == InferenceTier.DEEP

def test_deep_tier_code_review():
    assert classify_complexity("Please do a code review of this Python function") == InferenceTier.DEEP

def test_deep_tier_benchmark():
    assert classify_complexity("Benchmark my model performance and compare it") == InferenceTier.DEEP


# ── TieredIntelligenceRouter ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_router_fast_tier_streams():
    router = TieredIntelligenceRouter()
    tokens = []
    async for tok in router.route("Hello!", tier_override=InferenceTier.FAST):
        tokens.append(tok)
    assert len(tokens) > 0

@pytest.mark.asyncio
async def test_router_smart_tier_streams():
    router = TieredIntelligenceRouter()
    tokens = []
    async for tok in router.route("What is quantum computing?", tier_override=InferenceTier.SMART):
        tokens.append(tok)
    assert len(tokens) > 0

@pytest.mark.asyncio
async def test_router_deep_falls_back_when_colibri_offline():
    """
    When Colibri is offline (no local server), DEEP tier should gracefully
    fall back to SMART tier instead of crashing.
    """
    router = TieredIntelligenceRouter(colibri_base_url="http://localhost:9999")
    tokens = []
    async for tok in router.route("Analyze the entire system architecture in depth.", tier_override=InferenceTier.DEEP):
        tokens.append(tok)
    # Should not raise, should produce fallback message
    assert len(tokens) > 0
    full = "".join(tokens)
    assert "offline" in full.lower() or "simulated" in full.lower() or "LEO" in full

@pytest.mark.asyncio
async def test_routing_status_structure():
    router = TieredIntelligenceRouter(colibri_base_url="http://localhost:9999")
    status = await router.get_routing_status()
    assert "tier_fast"  in status
    assert "tier_smart" in status
    assert "tier_deep"  in status
    assert status["tier_deep"]["status"] == "offline"  # Colibri not running
