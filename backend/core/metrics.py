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
