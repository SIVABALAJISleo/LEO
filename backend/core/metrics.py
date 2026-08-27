from prometheus_client import REGISTRY, Summary as PromSummary, Gauge as PromGauge, Counter as PromCounter

def _metric(cls, name, doc, *args, **kwargs):
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    try:
        return cls(name, doc, *args, **kwargs)
    except ValueError:
        return REGISTRY._names_to_collectors.get(name, cls(name + "_v" + str(id(name)), doc, *args, **kwargs))

# Core System Metrics
REQUEST_TIME = _metric(PromSummary, 'request_processing_seconds', 'Time spent processing request')
CPU_USAGE = _metric(PromGauge, 'system_cpu_usage_percent', 'System CPU usage percentage')
GPU_USAGE = _metric(PromGauge, 'system_gpu_usage_percent', 'System GPU usage percentage (Mocked if no GPU)')

# Inference Avoidance Metrics
PPE_HITS = _metric(PromCounter, 'hyper_ppe_hits_total', 'Total Layer 1 PPE cache hits')
SHADOW_HITS = _metric(PromCounter, 'hyper_shadow_hits_total', 'Total Layer 0 Shadow cache hits')
TWIN_HITS = _metric(PromCounter, 'hyper_twin_hits_total', 'Total Layer 9 Digital Twin hits')
MODEL_INVOCATIONS = _metric(PromCounter, 'hyper_model_invocations_total', 'Total LLM ladder escalations')
AVOIDANCE_RATIO = _metric(PromGauge, 'hyper_inference_avoidance_ratio_v1', 'Ratio of requests avoiding full inference')
GPU_COST_SAVED = _metric(PromGauge, 'hyper_gpu_cost_saved_total', 'Estimated GPU cost saved in USD')

# Optimization Layer Metrics
RAG_HITS = _metric(PromCounter, 'hyper_rag_hits_total', 'Total retrieval attempts')
MICRO_MODEL_HITS = _metric(PromCounter, 'hyper_micro_model_hits_total', 'Total micro-model bypasses')
CACHE_HITS = _metric(PromCounter, 'hyper_cache_hits_total', 'Total prompt/semantic cache hits')

# Next-Gen Layer Metrics (10-Layer Pipeline)
GRAPH_HITS = _metric(PromCounter, 'hyper_graph_hits_total', 'Total Answer Graph Engine hits (Layer 1 bypass)')
TEMPLATE_HITS = _metric(PromCounter, 'hyper_template_hits_total', 'Total template compiler hits (zero model cost)')

# Enhancement Engine DLSS Metrics
ENHANCEMENT_ATTEMPTS = _metric(PromCounter, 'hyper_enhancement_attempts_total', 'Total answered evaluated for enhancement')
ENHANCEMENT_SUCCESS = _metric(PromCounter, 'hyper_enhancement_success_total', 'Total successful DLSS enhancements applied')
MODEL_BYPASS_VIA_ENHANCEMENT = _metric(PromCounter, 'hyper_model_bypass_via_enhancement', 'Total large-model calls bypassed due to enhancement')

# Adaptive Intelligence Controller (AIC) Metrics
AIC_SKIP_TOTAL = _metric(PromCounter, 'hyper_aic_skip_total', 'Total skips governed by dynamic AIC policy')
AIC_ESCALATION_TOTAL = _metric(PromCounter, 'hyper_aic_escalation_total', 'Total model escalations mandated by dynamic AIC policy')
INFERENCE_AVOIDANCE_RATIO = _metric(PromGauge, 'hyper_inference_avoidance_ratio_v2', 'Calculated dynamic inference avoidance ratio')

# SaaS Optimization Metrics
COST_SAVED_TOTAL = _metric(PromCounter, 'hyper_cost_saved_total', 'Total cumulative cost saved in USD')
ENHANCEMENT_HITS = _metric(PromCounter, 'hyper_enhancement_hits_total', 'Total successful AEE enhancements')
FUSION_HITS = _metric(PromCounter, 'hyper_fusion_hits_total', 'Total successful multi-source a-fusion events')
CONFIDENCE_BYPASS_RATE = _metric(PromGauge, 'hyper_confidence_bypass_rate', 'Real-time rate of confidence-based model bypasses')

MODEL_CALLS_TOTAL = _metric(PromCounter, 'hyper_model_calls_total', 'Total large model calls (last resort)')
LAST_RESORT_MODEL_USAGE = _metric(PromGauge, 'hyper_last_resort_model_usage_pct', 'Percentage of large model calls as a last resort')

REASONING_REUSES = _metric(PromCounter, 'hyper_reasoning_reuses_total', 'Total reasoning memory reuses')
EARLY_EXIT_TOTAL = _metric(PromCounter, 'hyper_early_exit_total', 'Total early-exit events from pipeline')
TOKEN_SAVINGS = _metric(PromGauge, 'hyper_token_savings_ratio', 'Average token reduction ratio from optimizer')

# Compute-Controlled System Metrics (12-Module Architecture)
CANONICAL_HITS = _metric(PromCounter, 'hyper_canonical_hits_total', 'Total canonical answer store hits (highest priority)')
PRECOMPUTE_HITS = _metric(PromCounter, 'hyper_precompute_hits_total', 'Total precomputed answer hits')
FAILURE_RATE = _metric(PromGauge, 'hyper_failure_rate', 'Rate of pipeline failures falling through to large model')
DOMAIN_REJECTIONS = _metric(PromCounter, 'hyper_domain_rejections_total', 'Total out-of-domain query rejections')
COST_FORCED_SAVES = _metric(PromCounter, 'hyper_cost_forced_saves_total', 'Total savings forced by cost controller')
LATENCY_SKIPS = _metric(PromCounter, 'hyper_latency_skips_total', 'Total layer skips by latency controller')

# Hyperscaler Performance Refinement
EMBEDDING_CACHE_HITS = _metric(PromCounter, 'hyper_embedding_cache_hits_total', 'Total redundant encoding bypasses')
TINY_MODEL_SUCCESS = _metric(PromCounter, 'hyper_tiny_model_success_total', 'Total queries resolved by CPU-first tiny models')
RUNTIME_COMPUTE_CALLS = _metric(PromCounter, 'hyper_runtime_compute_calls_total', 'Total runtime compute calls')

# Final System Strength Layer Metrics (Phase 30)
REUSE_RATE = _metric(PromGauge, 'hyper_reuse_rate_pct', 'Percentage of queries resolved via Global Memory or Graph')
UNKNOWN_ENQUEUE_RATE = _metric(PromGauge, 'hyper_unknown_enqueue_rate_pct', 'Percentage of unknown queries safely enqueued')
APPROXIMATION_ACCURACY = _metric(PromGauge, 'hyper_approximation_accuracy_pct', 'Perceptual accuracy of adaptive approximations')
