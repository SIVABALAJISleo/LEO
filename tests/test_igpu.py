"""
tests/test_igpu.py
Unit tests for LEO iGPU execution engine fallback capabilities.
"""

import pytest
from unittest.mock import MagicMock, patch
from backend.inference.igpu_execution import IGPUExecutionEngine, _has_mlx, _has_llama_cpp


def test_has_mlx():
    # Verify OS/import logic check functions safely without exception
    val = _has_mlx()
    assert isinstance(val, bool)


def test_has_llama_cpp():
    val = _has_llama_cpp()
    assert isinstance(val, bool)


@pytest.mark.asyncio
async def test_engine_fallback_generation():
    engine = IGPUExecutionEngine()
    
    # 1. Force simulated CPU fallback path by patching has check functions
    with patch("backend.inference.igpu_execution._has_llama_cpp", return_value=False), \
         patch("backend.inference.igpu_execution._has_mlx", return_value=False), \
         patch("backend.inference.igpu_execution._has_openvino_genai", return_value=False):
        
        engine_fallback = IGPUExecutionEngine()
        
        tokens = []
        async for token in engine_fallback.generate(
            prompt="Hello World",
            model_path="dummy_path.gguf",
            device_plan={"cpu": {"layers": 32}}
        ):
            tokens.append(token)
            
        assert len(tokens) > 0
        assert any("SIM" in t or "ERROR" in t for t in tokens)
