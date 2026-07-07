"""
tests/test_speculative.py
Unit tests for Layer 3 Speculative Decoding and Predictive Prefetch API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.inference.speculative_decoder import SpeculativeDecoder

client = TestClient(app)


def test_prompt_lookup_n_grams():
    decoder = SpeculativeDecoder()
    prompt = "This is a detailed document describing how LEO AI works on standard CPU hardware."
    
    # Extract follow-up tokens
    n_grams = decoder.extract_prompt_n_grams(prompt, prefix="how LEO AI", n=3)
    assert len(n_grams) == 3
    assert n_grams == ["works", "on", "standard"]


@pytest.mark.asyncio
async def test_speculative_stream():
    decoder = SpeculativeDecoder()
    tokens = []
    async for token in decoder.generate_stream(
        prompt="Explain LEO swarm",
        max_tokens=10,
        use_prompt_lookup=False
    ):
        tokens.append(token)
        
    assert len(tokens) > 0
    assert any("future" in t or "LEO" in t or "and" in t for t in tokens)


def test_prefetch_api_flow():
    session_id = "test_prefetch_session"
    
    # 1. Trigger prefetch
    res = client.post(
        "/api/v1/prefetch",
        json={"session_id": session_id, "partial_query": "Explain LEO"}
    )
    assert res.status_code == 200
    assert res.json()["status"] == "success"
    assert res.json()["completed_guess"] == "Explain LEO architecture"

    # 2. Check prefetch (Successful match)
    res_check = client.post(
        "/api/v1/prefetch/check",
        json={"session_id": session_id, "final_query": "Explain LEO architecture"}
    )
    assert res_check.status_code == 200
    assert res_check.json()["hit"] is True
    assert "future" in res_check.json()["response"] or "LEO" in res_check.json()["response"] or "and" in res_check.json()["response"]


def test_prefetch_api_miss():
    session_id = "test_prefetch_session_miss"
    
    # Trigger prefetch
    client.post(
        "/api/v1/prefetch",
        json={"session_id": session_id, "partial_query": "Explain LEO"}
    )

    # Check prefetch with completely unrelated query (Miss)
    res_check = client.post(
        "/api/v1/prefetch/check",
        json={"session_id": session_id, "final_query": "What is the weather like?"}
    )
    assert res_check.status_code == 200
    assert res_check.json()["hit"] is False
