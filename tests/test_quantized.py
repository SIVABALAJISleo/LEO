"""
tests/test_quantized.py
Unit tests for Layer 2 Quantized Execution Engine and T-MAC lookup table GEMM.
"""

import pytest
import numpy as np
from backend.inference.quantized_engine import QuantizedExecutionEngine
from backend.inference.sparse_engine import emulate_tmac_lut_matmul


def test_quantization_select():
    engine = QuantizedExecutionEngine()
    
    # Verify cascade selections
    assert engine.select_best_quantization(0.99) == "FP16"
    assert engine.select_best_quantization(0.90) == "INT8"
    assert engine.select_best_quantization(0.75) == "INT4"
    assert engine.select_best_quantization(0.50) == "TERNARY"


def test_emulate_tmac_lut_matmul():
    # Setup simple weights and activations
    weights = np.array([[1.0, -1.0], [0.5, 0.5]], dtype=np.float32)
    activations = np.array([2.0, 4.0], dtype=np.float32)
    
    # Emulate T-MAC lookup GEMM multiplication (2-bit quantization)
    result = emulate_tmac_lut_matmul(weights, activations, bits=2)
    
    assert isinstance(result, np.ndarray)
    assert result.shape == (2,)


@pytest.mark.asyncio
async def test_quantized_generate():
    engine = QuantizedExecutionEngine()
    
    # 1. Test FP16 generation path
    tokens_fp16 = []
    async for token in engine.generate(
        prompt="Test",
        model_path="dummy_model",
        device_plan={"required_accuracy": 0.99}
    ):
        tokens_fp16.append(token)
    assert len(tokens_fp16) > 0
    assert any("FP16" in t for t in tokens_fp16)

    # 2. Test TERNARY generation path
    tokens_ternary = []
    async for token in engine.generate(
        prompt="Test",
        model_path="dummy_model",
        device_plan={"required_accuracy": 0.50}
    ):
        tokens_ternary.append(token)
    assert len(tokens_ternary) > 0
    assert any("ternary" in t or "rapid" in t or "BitNet" in t for t in tokens_ternary)
