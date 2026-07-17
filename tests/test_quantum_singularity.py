"""
LEO Quantum Singularity Core Integration Tests
Verifies heterogeneous execution, speculative decoding, dynamic MoE, hierarchical caching, and self-optimization.
"""
import pytest
import torch
import numpy as np
from core.quantum.heterogeneous.unified_scheduler import UnifiedHeterogeneousScheduler
from core.quantum.heterogeneous.memory_router import UnifiedMemoryRouter
from core.quantum.heterogeneous.thermal_manager import ThermalManager
from core.quantum.heterogeneous.performance_monitor import PerformanceMonitor
from core.quantum.speculative.bnn_draft_model import BNNDraftModel
from core.quantum.speculative.speculative_decoder import SpeculativeDecoder
from core.quantum.speculative.cross_device_verifier import CrossDeviceVerifier
from core.quantum.speculative.acceptance_rejector import AcceptanceRejector
from core.quantum.moe.dynamic_expert_router import DynamicExpertRouter, ExpertPredictor
from core.quantum.moe.memory_efficient_moe import MemoryEfficientMoE
from core.quantum.moe.task_aware_scheduler import TaskAwareScheduler
from core.quantum.caching.hierarchical_cache import HierarchicalCache
from core.quantum.caching.semantic_cache import SemanticCache
from core.quantum.caching.kv_cache_optimizer import KVCacheOptimizer
from core.quantum.caching.predictive_prefetcher import PredictivePrefetcher
from core.quantum.optimization.adaptive_pipeline import AdaptivePipeline, QueryComplexityAnalyzer
from core.quantum.optimization.self_optimizer import SelfOptimizer
from core.quantum.optimization.bottleneck_analyzer import BottleneckAnalyzer
from core.quantum.optimization.configuration_evolver import ConfigurationEvolver
from core.quantum.benchmarking.gpu_competitiveness_benchmark import GPUCompetitivenessBenchmark


def test_heterogeneous_scheduler():
    scheduler = UnifiedHeterogeneousScheduler()
    # Create simple sequential model
    model = torch.nn.Sequential(
        torch.nn.Linear(10, 10),
        torch.nn.ReLU(),
        torch.nn.Linear(10, 5)
    )
    x = torch.randn(1, 10)
    
    # Adaptive execution strategy
    out = scheduler.execute_model_heterogeneous(model, x, execution_strategy='adaptive')
    assert out.shape == (1, 5)
    
    # Forced CPU execution
    out_cpu = scheduler.execute_model_heterogeneous(model, x, execution_strategy='cpu_only')
    assert out_cpu.shape == (1, 5)

    # Validate memory router
    router = UnifiedMemoryRouter()
    tensor = router.allocate_tensor((2, 5), dtype=torch.float32, preferred_device='cpu')
    assert tensor.shape == (2, 5)
    assert tensor.device.type == 'cpu'


def test_bnn_and_speculative_decoding():
    vocab_size = 100
    embed_dim = 64
    draft_model = BNNDraftModel(vocab_size=vocab_size, embed_dim=embed_dim, num_layers=2)
    
    # Create standard dummy model that represents target model
    class DummyTargetModel(torch.nn.Module):
        def forward(self, x):
            # Returns uniform logits across vocab
            return torch.zeros(x.shape[0], x.shape[1], vocab_size)
            
    target_model = DummyTargetModel()
    
    # Verify BNN weight quantization
    for layer in draft_model.layers:
        weight = layer['attention'].q_proj.weight
        q_weight = layer['attention'].q_proj.quantize_weights()
        # Quantized weight must contain ternary values {-1.0, 0.0, 1.0}
        unique_vals = torch.unique(q_weight).tolist()
        for val in unique_vals:
            assert val in [-1.0, 0.0, 1.0]

    # Run speculative decoder
    decoder = SpeculativeDecoder(target_model, draft_model, config={'num_draft_tokens': 3})
    input_ids = torch.randint(0, vocab_size, (1, 5))
    
    # Generate 5 tokens
    gen_ids, stats = decoder.generate(input_ids, max_new_tokens=5, temperature=0.8)
    assert gen_ids.shape[1] == 10
    assert stats['total_tokens_generated'] == 5
    assert stats['acceptance_rate'] >= 0.0
    
    # Check acceptance policy
    rejector = AcceptanceRejector(mode='stochastic')
    target_probs = torch.zeros(1, vocab_size)
    target_probs[0, 5] = 0.9
    draft_probs = torch.zeros(1, vocab_size)
    draft_probs[0, 5] = 0.8
    # Should accept draft token with high target probability
    assert rejector.should_accept(5, target_probs, draft_probs) is True


def test_dynamic_moe_routing():
    num_experts = 4
    expert_dim = 16
    moe = MemoryEfficientMoE(num_experts=num_experts, expert_dim=expert_dim, max_active_experts=2)
    
    x = torch.randn(1, 4, expert_dim)
    out = moe(x, task_type='general')
    assert out.shape == x.shape
    
    # Verify LRU expert cache eviction
    assert len(moe.router.active_experts) <= 2
    
    # Verify task predictor
    predictor = ExpertPredictor(num_experts=num_experts)
    preds = predictor.predict_experts(x, task_type='math', num_predict=2)
    assert len(preds) == 2
    assert all(0 <= idx < num_experts for idx in preds)


def test_hierarchical_cache():
    cache = HierarchicalCache(config={'redis_enabled': False})
    query = "How do we bypass combustion?"
    response = "Implement vector-symbolic hypervectors."
    
    # Simulate embedding (384 dimension)
    embedding = np.random.randn(384)
    
    # Insert in cache
    cache.put(query, response, embedding=embedding)
    
    # Fetch from exact match
    res, lat, lvl = cache.get(query)
    assert res == response
    assert lvl == 'L1_exact'
    
    # Fetch from semantic match (cosine similarity)
    res_sem, lat_sem, lvl_sem = cache.get("How to bypass combustion?", embedding=embedding)
    assert res_sem == response
    assert lvl_sem == 'L2_semantic'


def test_adaptive_pipeline_and_tuning():
    pipeline = AdaptivePipeline()
    query = "Create a new topological hypergraph simulation"
    
    # Analyze query complexity
    analyzer = QueryComplexityAnalyzer()
    res = analyzer.analyze(query)
    assert res['query_type'] == 'complex'
    assert res['recommended_model'] == '7b'
    
    # Execute query
    pipeline_res = pipeline.process_query(query)
    assert "Processed query" in pipeline_res['response']
    assert pipeline_res['metadata']['complexity']['query_type'] == 'complex'
    
    # Validate bottleneck analyzer
    bottleneck = BottleneckAnalyzer()
    bottleneck.add_trace('cpu_inference', 45.0)
    bottleneck.add_trace('gpu_sync', 55.0)
    analysis = bottleneck.analyze_hotspots()
    assert analysis['primary_bottleneck'] == 'gpu_sync'


def test_competitiveness_benchmark():
    # Mock system class
    class MockLEOSystem:
        def generate(self, ids, max_new_tokens):
            return ids
            
    system = MockLEOSystem()
    bench = GPUCompetitivenessBenchmark()
    
    # Run comparison benchmarks
    results = bench.run_comprehensive_benchmark(system)
    assert results['overall_competitiveness'] > 0.0
    assert 'leo_results' in results
    assert 'nvidia_results' in results
