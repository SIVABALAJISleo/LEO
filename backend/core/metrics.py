from prometheus_client import Summary, Gauge, Counter as PromCounter

# Core System Metrics
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
CPU_USAGE = Gauge('system_cpu_usage_percent', 'System CPU usage percentage')
GPU_USAGE = Gauge('system_gpu_usage_percent', 'System GPU usage percentage (Mocked if no GPU)')

# Inference Avoidance Metrics
PPE_HITS = PromCounter('hyper_ppe_hits_total', 'Total Layer 1 PPE cache hits')
SHADOW_HITS = PromCounter('hyper_shadow_hits_total', 'Total Layer 0 Shadow cache hits')
TWIN_HITS = PromCounter('hyper_twin_hits_total', 'Total Layer 9 Digital Twin hits')
MODEL_INVOCATIONS = PromCounter('hyper_model_invocations_total', 'Total LLM ladder escalations')
AVOIDANCE_RATIO = Gauge('hyper_inference_avoidance_ratio', 'Ratio of requests avoiding full inference')
GPU_COST_SAVED = Gauge('hyper_gpu_cost_saved_total', 'Estimated GPU cost saved in USD')

# Optimization Layer Metrics
RAG_HITS = PromCounter('hyper_rag_hits_total', 'Total retrieval attempts')
MICRO_MODEL_HITS = PromCounter('hyper_micro_model_hits_total', 'Total micro-model bypasses')
CACHE_HITS = PromCounter('hyper_cache_hits_total', 'Total prompt/semantic cache hits')

# Next-Gen Layer Metrics (10-Layer Pipeline)
GRAPH_HITS = PromCounter('hyper_graph_hits_total', 'Total Answer Graph Engine hits (Layer 1 bypass)')
TEMPLATE_HITS = PromCounter('hyper_template_hits_total', 'Total template compiler hits (zero model cost)')

# Enhancement Engine DLSS Metrics
ENHANCEMENT_ATTEMPTS = PromCounter('hyper_enhancement_attempts_total', 'Total answered evaluated for enhancement')
ENHANCEMENT_SUCCESS = PromCounter('hyper_enhancement_success_total', 'Total successful DLSS enhancements applied')
MODEL_BYPASS_VIA_ENHANCEMENT = PromCounter('hyper_model_bypass_via_enhancement', 'Total large-model calls bypassed due to enhancement')

MODEL_CALLS_TOTAL = PromCounter('hyper_model_calls_total', 'Total large model calls (last resort)')

REASONING_REUSES = PromCounter('hyper_reasoning_reuses_total', 'Total reasoning memory reuses')
EARLY_EXIT_TOTAL = PromCounter('hyper_early_exit_total', 'Total early-exit events from pipeline')
TOKEN_SAVINGS = Gauge('hyper_token_savings_ratio', 'Average token reduction ratio from optimizer')

# Compute-Controlled System Metrics (12-Module Architecture)
CANONICAL_HITS = PromCounter('hyper_canonical_hits_total', 'Total canonical answer store hits (highest priority)')
PRECOMPUTE_HITS = PromCounter('hyper_precompute_hits_total', 'Total precomputed answer hits')
FAILURE_RATE = Gauge('hyper_failure_rate', 'Rate of pipeline failures falling through to large model')
DOMAIN_REJECTIONS = PromCounter('hyper_domain_rejections_total', 'Total out-of-domain query rejections')
COST_FORCED_SAVES = PromCounter('hyper_cost_forced_saves_total', 'Total savings forced by cost controller')
LATENCY_SKIPS = PromCounter('hyper_latency_skips_total', 'Total layer skips by latency controller')
