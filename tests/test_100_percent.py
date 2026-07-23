import pytest
import numpy as np
import sys
import os

# Add root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.paradigm_bypass.layer1_binary_resonance import BinaryNeuralNetwork, HyperdimensionalResonanceEngine
from core.paradigm_bypass.layer2_anomaly_driven import AnomalyDrivenProcessor
from core.paradigm_bypass.layer3_virtual_memory import InfiniteMemoryArchitecture
from core.paradigm_bypass.layer4_system_parallelism import SystemTopologyDetector
from core.paradigm_bypass.orchestrator import LEO_100_Percent_Engine

def test_layer1_binary_resonance():
    bnn = BinaryNeuralNetwork(128)
    x = np.random.randn(128)
    out = bnn.forward(x)
    assert out.shape == (128,)
    assert np.all(out >= 0)

    hd = HyperdimensionalResonanceEngine(dim=1024)
    res = hd.resonance_match("test query")
    assert res == "test query"

def test_layer2_anomaly_processor():
    processor = AnomalyDrivenProcessor(threshold=0.1)
    input_a = np.ones(10)
    input_b = np.ones(10) + 0.05  # Delta < threshold
    input_c = np.ones(10) + 0.5   # Delta > threshold

    out_a = processor.process(input_a)
    assert processor.compute_count == 1

    out_b = processor.process(input_b)
    assert processor.skip_count == 1
    assert np.array_equal(out_b, input_a)  # Should return last state

    out_c = processor.process(input_c)
    assert processor.compute_count == 2
    assert not np.array_equal(out_c, input_a)

def test_layer3_virtual_memory(tmp_path):
    mem = InfiniteMemoryArchitecture(disk_path=str(tmp_path), cache_size_gb=1)
    data = np.array([1.0, 2.0, -1.0])
    mem.store("test_key", data)
    
    retrieved = mem.retrieve("test_key")
    assert retrieved is not None
    assert len(retrieved) == 10000  # Default HD dim

def test_layer4_topology():
    detector = SystemTopologyDetector()
    top = detector.get_topology()
    assert top["p_cores"] == 4
    assert top["e_cores"] == 4
    assert top["igpu_eus"] == 24

def test_100_percent_engine_process():
    engine = LEO_100_Percent_Engine()
    result = engine.process({"query": "hello world", "type": "generic"})
    assert "hello world" in result
    assert "[Enhanced Quality]" in result

def test_benchmark_100_percent_method():
    engine = LEO_100_Percent_Engine()
    report = engine.benchmark_100_percent()
    assert report["score"] >= 1.0
    assert report["status"] == "100% ACHIEVED"
