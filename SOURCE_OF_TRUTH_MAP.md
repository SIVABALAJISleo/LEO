# LEO/HYPER Source of Truth Map

## Executive Architectural Decision

The repository contains historical prototypes across `archive_engines/`, `core_ai/`, `backend/`, `HYPER_v6_BREAKTHROUGH/`, and `hyper_x/`.
Under the **Verified Computation-Elimination Runtime Architecture**, the unified and authoritative package is **`hyper/`**.
All older and experimental implementations are classified as `DEPRECATED` or `EXPERIMENTAL` and preserved for reference without compromising scientific integrity.

## Authoritative Source of Truth Matrix

| Subsystem | Authoritative Module (`hyper/`) | Legacy / Prototype Locations | Status | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| **Contracts & Constraints** | `hyper.contracts.contract` | `contracts/`, `core_ai/contracts.py` | ACTIVE_SOURCE | Enforce formal `Contract` dataclass with fail-closed validation |
| **Hardware Profiler** | `hyper.cli` / `hyper.hardware` | `benchmarks/hardware_check.py`, `scripts/bench_hardware.py` | ACTIVE_SOURCE | Dynamic profiling via `python -m hyper.cli hardware-profile` |
| **Candidate Execution Model** | `hyper.candidate` | `core_ai/router.py`, `universal_compute_router/` | ACTIVE_SOURCE | Explicit `CandidateResult` with paths (`EXACT`, `CACHED`, etc.) |
| **Exact Cache** | `hyper.cache` | `archive_engines/.../cache.py`, `cache/` | ACTIVE_SOURCE | Multi-state cryptographic hash; separate hit/miss reporting |
| **Incremental & Delta** | `hyper.incremental` | `archive_engines/temporal_engine.py` | ACTIVE_SOURCE | Linear delta reuse with exact fallback on nonlinear/unknown |
| **Sparsity Engine** | `hyper.sparsity` | `core_ai/sparsity.py`, `optimization/sparsity.py` | ACTIVE_SOURCE | Measure threshold overhead; only run if cheaper than dense |
| **Low-Rank Factorization** | `hyper.low_rank` | `math_engine/svd.py`, `backend/compression/` | ACTIVE_SOURCE | SVD with break-even reuse count tracking |
| **Precision Engine** | `hyper.precision` | `core_ai/quantization.py`, `scripts/compress_to_ternary.py` | ACTIVE_SOURCE | Explicit multi-precision (FP64 down to ternary) with error bounds |
| **Prediction & Residual** | `hyper.prediction` / `hyper.residual` | `core_ai/speculative_engine.py`, `predictors/` | ACTIVE_SOURCE | Contract-verified $\hat{y} + r$ with exact fallback |
| **CPU + iGPU Scheduler** | `hyper.scheduler` | `universal_compute_router/orchestrator.py`, `hyper_ares/` | ACTIVE_SOURCE | Real benchmark-driven dispatch between CPU and Intel UHD iGPU |
| **Verification Engine** | `hyper.verification` | `archive_engines/.../verifier.py`, `qa_security_team/` | ACTIVE_SOURCE | Multi-domain (Freivalds, PSNR/SSIM, retrieval, exact numerical) |
| **Benchmarking Suite** | `hyper.benchmark` | `scripts/benchmark.py`, `benchmarks/` | ACTIVE_SOURCE | High-resolution `perf_counter_ns()`, warmups, p95, zero fake timings |
| **Parity Calculations** | `hyper.parity` | `scripts/verify_100_percent.py` | ACTIVE_SOURCE | Disjoint tiers (`RAW_HARDWARE`, `CONTRACT`, `APPLICATION`) |

## Detailed Duplicate Module Inventory

### Module `adaptive_router.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/project_hyper/router/adaptive_router.py` | `DEPRECATED` | 724 | `hardness` | Preserve as historical reference (Deprecated) |
| `backend/layer4_router/adaptive_router.py` | `ACTIVE_SOURCE` | 17309 | `backend.layer10_metrics.telemetry, backend.layer1_memory.semantic_cache, backend.layer2_crystallize.crystallizer, backend.layer3_retrieval.rag_engine` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/routing/adaptive_router.py` | `ACTIVE_SOURCE` | 3496 | `logging, re, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `adversarial.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `cbe/validation/adversarial.py` | `ACTIVE_SOURCE` | 8760 | `__future__, cbe.controller.cbe_controller, cbe.controller.quality_controller, cbe.state.object_state` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/verification/adversarial.py` | `EXPERIMENTAL` | 368 | `numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/verification/adversarial.py` | `ACTIVE_SOURCE` | 2956 | `numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `analyzer.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/closed_loop_synthesis/core/analyzer.py` | `DEPRECATED` | 1695 | `re` | Preserve as historical reference (Deprecated) |
| `hyper/workload/analyzer.py` | `ACTIVE_SOURCE` | 2557 | `graph, numpy, typing` | **Retain as Authoritative Source of Truth** |
| `information_sufficiency/analyzer.py` | `ACTIVE_SOURCE` | 6975 | `enum, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `answer_store.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/learning/answer_store.py` | `ACTIVE_SOURCE` | 3572 | `backend.core.database, backend.graph.fragment_graph, backend.intelligence.router, backend.memory.global_memory` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/predictive/answer_store.py` | `ACTIVE_SOURCE` | 3302 | `backend.core.database, backend.intelligence.router, logging, numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `api.py` (25 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `api.py` | `ACTIVE_SOURCE` | 2098 | `archive_engines.router.routing_logic, archive_engines.verifier.validation, backend.hardware.gna_guardrail, core.input_logic` | Preserve for compatibility / migrate to `hyper.*` |
| `archive_engines/adaptive_compute_router/api.py` | `DEPRECATED` | 2051 | `archive_engines.adaptive_compute_router.kernel, fastapi, fastapi.responses, intel_core_ai.inference` | Preserve as historical reference (Deprecated) |
| `archive_engines/adaptive_self_correcting_system/api.py` | `DEPRECATED` | 785 | `core.orchestrator, fastapi, models.schemas, pydantic` | Preserve as historical reference (Deprecated) |
| `archive_engines/adversarial_verification_system/api.py` | `DEPRECATED` | 2897 | `archive_engines.adversarial_verification_system.core.breaker, archive_engines.adversarial_verification_system.core.proposer, archive_engines.adversarial_verification_system.core.verifier, fastapi` | Preserve as historical reference (Deprecated) |
| `archive_engines/boundary_perfect_ai/api.py` | `DEPRECATED` | 2274 | `archive_engines.boundary_perfect_ai.kernel, fastapi, fastapi.responses, intel_core_ai.inference` | Preserve as historical reference (Deprecated) |
| `archive_engines/composable_intel_ai/api.py` | `DEPRECATED` | 3160 | `archive_engines.composable_intel_ai.adapter_manager, archive_engines.composable_intel_ai.soft_router, archive_engines.hybrid_intel_ai.knowledge, archive_engines.hybrid_intel_ai.symbolic` | Preserve as historical reference (Deprecated) |
| `archive_engines/controlled_ai_pipeline/api.py` | `DEPRECATED` | 2215 | `archive_engines.controlled_ai_pipeline.kernel, archive_engines.high_perf_intel_ai.inference, archive_engines.llm_os_core.memory_knowledge, fastapi` | Preserve as historical reference (Deprecated) |
| `archive_engines/high_accuracy_engine/api.py` | `DEPRECATED` | 2387 | `archive_engines.high_accuracy_engine.kernel, fastapi, fastapi.responses, intel_core_ai.inference` | Preserve as historical reference (Deprecated) |
| `archive_engines/high_perf_intel_ai/api.py` | `DEPRECATED` | 2876 | `archive_engines.high_perf_intel_ai.inference, archive_engines.high_perf_intel_ai.kernel, archive_engines.llm_os_core.memory_knowledge, archive_engines.vulkan_intel_ai.cache` | Preserve as historical reference (Deprecated) |
| `archive_engines/hybrid_intel_ai/api.py` | `DEPRECATED` | 3610 | `archive_engines.hybrid_intel_ai.evaluator, archive_engines.hybrid_intel_ai.knowledge, archive_engines.hybrid_intel_ai.router, archive_engines.hybrid_intel_ai.symbolic` | Preserve as historical reference (Deprecated) |
| `archive_engines/hybrid_os_symbolic/api.py` | `DEPRECATED` | 2112 | `archive_engines.hybrid_os_symbolic.kernel, archive_engines.llm_os_core.memory_knowledge, fastapi, fastapi.responses` | Preserve as historical reference (Deprecated) |
| `archive_engines/hyper_core_ai/api.py` | `DEPRECATED` | 5802 | `archive_engines.hyper_core_ai.memory, archive_engines.llm_os_core.execution, intel_core_ai.inference, logging` | Preserve as historical reference (Deprecated) |
| `archive_engines/llm_os_core/api.py` | `DEPRECATED` | 3163 | `archive_engines.llm_os_core.execution, archive_engines.llm_os_core.memory_knowledge, fastapi, fastapi.responses` | Preserve as historical reference (Deprecated) |
| `archive_engines/llm_os_intel/api.py` | `DEPRECATED` | 2928 | `archive_engines.hybrid_intel_ai.knowledge, archive_engines.llm_os_intel.memory, archive_engines.llm_os_intel.reasoning_loop, fastapi` | Preserve as historical reference (Deprecated) |
| `archive_engines/outcome_driven_ai/api.py` | `DEPRECATED` | 2015 | `archive_engines.outcome_driven_ai.kernel, fastapi, fastapi.responses, intel_core_ai.inference` | Preserve as historical reference (Deprecated) |
| `archive_engines/perfect_verification_system/api.py` | `DEPRECATED` | 3713 | `archive_engines.perfect_verification_system.config, archive_engines.perfect_verification_system.core.cache, archive_engines.perfect_verification_system.core.mutation_engine, archive_engines.perfect_verification_system.core.proposer` | Preserve as historical reference (Deprecated) |
| `archive_engines/safe_outcome_ai/api.py` | `DEPRECATED` | 2451 | `archive_engines.safe_outcome_ai.kernel, fastapi, fastapi.responses, intel_core_ai.inference` | Preserve as historical reference (Deprecated) |
| `archive_engines/self_skeptical_engine/api.py` | `DEPRECATED` | 2488 | `archive_engines.self_skeptical_engine.kernel, fastapi, fastapi.responses, intel_core_ai.inference` | Preserve as historical reference (Deprecated) |
| `archive_engines/steered_intel_ai/api.py` | `DEPRECATED` | 3396 | `archive_engines.hybrid_intel_ai.knowledge, archive_engines.steered_intel_ai.router, archive_engines.steered_intel_ai.steering_engine, archive_engines.steered_intel_ai.tools` | Preserve as historical reference (Deprecated) |
| `archive_engines/verified_outcome_ai/api.py` | `DEPRECATED` | 2589 | `archive_engines.verified_outcome_ai.kernel, fastapi, fastapi.responses, intel_core_ai.inference` | Preserve as historical reference (Deprecated) |
| `archive_engines/vulkan_intel_ai/api.py` | `DEPRECATED` | 3778 | `archive_engines.llm_os_core.memory_knowledge, archive_engines.vulkan_intel_ai.cache, archive_engines.vulkan_intel_ai.inference, archive_engines.vulkan_intel_ai.kernel` | Preserve as historical reference (Deprecated) |
| `core_ai/api.py` | `ACTIVE_SOURCE` | 4908 | `core_ai.input_control, core_ai.intent_layer, core_ai.knowledge_layer, core_ai.pipeline_components` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/frontend/api.py` | `EXPERIMENTAL` | 1063 | `hyper_v3.frontend.contract_parser, hyper_v3.frontend.program_observer, hyper_v3.frontend.workload_loader, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `intel_core_ai/api.py` | `ACTIVE_SOURCE` | 3061 | `fastapi, fastapi.responses, intel_core_ai.inference, intel_core_ai.input_logic` | Preserve for compatibility / migrate to `hyper.*` |
| `universal_compute_router/api.py` | `ACTIVE_SOURCE` | 1999 | `fastapi, fastapi.responses, intel_core_ai.inference, json` | Preserve for compatibility / migrate to `hyper.*` |

### Module `backup_db.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `scripts/backup_db.py` | `ACTIVE_SOURCE` | 1617 | `boto3, datetime, logging, os` | Preserve for compatibility / migrate to `hyper.*` |
| `scripts/maintenance/backup_db.py` | `ACTIVE_SOURCE` | 1058 | `datetime, os, sqlite3` | Preserve for compatibility / migrate to `hyper.*` |

### Module `behavior_emulation.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/engine_hv/advanced/behavior_emulation.py` | `DEPRECATED` | 2653 | `json, logging, os, typing` | Preserve as historical reference (Deprecated) |
| `experts/behavior_emulation.py` | `ACTIVE_SOURCE` | 1659 | `logging, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `benchmark.py` (4 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/benchmark.py` | `BENCHMARK` | 10202 | `asyncio, backend.analytics.avoidance_tracker, backend.core.ais_pipeline, backend.core.database` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/routers/benchmark.py` | `BENCHMARK` | 939 | `backend.benchmarks.engine, fastapi, pydantic, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `scripts/benchmark.py` | `BENCHMARK` | 4234 | `asyncio, backend.analytics.metrics, backend.core.stability_layer, json` | Preserve for compatibility / migrate to `hyper.*` |
| `tests/benchmark.py` | `TEST` | 2655 | `asyncio, backend.analytics.metrics, backend.core.orchestrator, os` | Update imports to reference `hyper.*` |

### Module `benchmark_runner.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_runtime/telemetry/benchmark_runner.py` | `BENCHMARK` | 606 | `telemetry, time` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v2/audit/benchmark_runner.py` | `BENCHMARK` | 2176 | `hyper_v2.compiler.contract_compiler, hyper_v2.execution.device_manager, hyper_v2.workloads.suite_15, json` | Preserve for compatibility / migrate to `hyper.*` |

### Module `benchmark_suite.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `HYPER_v6_BREAKTHROUGH/benchmark_suite.py` | `BENCHMARK` | 9259 | `core_ai.alchemy_engine, hyper_engine, json, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper100/benchmarks/benchmark_suite.py` | `BENCHMARK` | 32668 | `algorithmic_reformulation, cache_reuse_engine, contract_engine, dataclasses` | Preserve for compatibility / migrate to `hyper.*` |

### Module `bitnet_engine.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/layer5_local_infer/bitnet_engine.py` | `ACTIVE_SOURCE` | 2812 | `bitnet_cpp, logging, os, time` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/bitnet_engine.py` | `ACTIVE_SOURCE` | 4885 | `json, logging, numpy, os` | Preserve for compatibility / migrate to `hyper.*` |

### Module `breaker.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/agents/breaker.py` | `DEPRECATED` | 1319 | `models.schemas` | Preserve as historical reference (Deprecated) |
| `archive_engines/adversarial_verification_system/core/breaker.py` | `DEPRECATED` | 1041 | `typing` | Preserve as historical reference (Deprecated) |

### Module `cache.py` (8 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/core/cache.py` | `DEPRECATED` | 1254 | `datetime, numpy, typing` | Preserve as historical reference (Deprecated) |
| `archive_engines/closed_loop_synthesis/core/cache.py` | `DEPRECATED` | 2366 | `archive_engines.closed_loop_synthesis.config, faiss, json, logging` | Preserve as historical reference (Deprecated) |
| `archive_engines/orchestration/cache.py` | `DEPRECATED` | 1950 | `hashlib, json, logging, typing` | Preserve as historical reference (Deprecated) |
| `archive_engines/perfect_verification_system/core/cache.py` | `DEPRECATED` | 1125 | `faiss, sentence_transformers, typing` | Preserve as historical reference (Deprecated) |
| `archive_engines/vulkan_intel_ai/cache.py` | `DEPRECATED` | 1448 | `faiss, logging, numpy, sentence_transformers` | Preserve as historical reference (Deprecated) |
| `backend/hybrid/cache.py` | `ACTIVE_SOURCE` | 2547 | `faiss, json, logging, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/memory/cache.py` | `EXPERIMENTAL` | 1986 | `collections, hashlib, json, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `project_hyper/cache.py` | `ACTIVE_SOURCE` | 1076 | `faiss, numpy, sentence_transformers` | Preserve for compatibility / migrate to `hyper.*` |

### Module `certificate.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_cco/certificate.py` | `ACTIVE_SOURCE` | 5519 | `contract, dataclasses, hashlib, json` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/certificates/certificate.py` | `ACTIVE_SOURCE` | 5182 | `__future__, dataclasses, enum, hashlib` | Preserve for compatibility / migrate to `hyper.*` |

### Module `chaos.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/core/chaos.py` | `ACTIVE_SOURCE` | 1184 | `asyncio, backend.core.orchestrator, logging` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/failure/chaos.py` | `ACTIVE_SOURCE` | 823 | `random` | Preserve for compatibility / migrate to `hyper.*` |

### Module `claim_validator.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_cco/claim_validator.py` | `ACTIVE_SOURCE` | 3840 | `__future__, dataclasses, re, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/claim_validator.py` | `ACTIVE_SOURCE` | 4170 | `__future__, dataclasses, enum, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `classifier.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/core/classifier.py` | `DEPRECATED` | 1122 | `models.schemas` | Preserve as historical reference (Deprecated) |
| `backend/intent/classifier.py` | `ACTIVE_SOURCE` | 4700 | `logging, math, re, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `cli.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `cbe/cli.py` | `ACTIVE_SOURCE` | 10862 | `__future__, cbe.controller, cbe.telemetry, cbe.validation` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/cli.py` | `ACTIVE_SOURCE` | 34050 | `__future__, argparse, hashlib, hyper_cco.coverage_engine` | Preserve for compatibility / migrate to `hyper.*` |

### Module `compiler.py` (4 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/gatekeeper_architecture/compiler/compiler.py` | `DEPRECATED` | 3613 | `hashlib, json, os` | Preserve as historical reference (Deprecated) |
| `hyper_x/info_boundary/compiler.py` | `ACTIVE_SOURCE` | 7911 | `__future__, dataclasses, enum, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/necessity/compiler.py` | `ACTIVE_SOURCE` | 6719 | `numpy, typing, work_ledger` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/compiler.py` | `ACTIVE_SOURCE` | 18576 | `__future__, hashlib, hyper_x.hardware.fingerprint, hyper_x.wormhole_compiler.algorithm_grammar` | Preserve for compatibility / migrate to `hyper.*` |

### Module `complexity.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_mvc_dar/complexity.py` | `ACTIVE_SOURCE` | 1977 | `contract, math, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/intelligence/complexity.py` | `EXPERIMENTAL` | 1534 | `math, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `components.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/high_accuracy_engine/components.py` | `DEPRECATED` | 1562 | `intel_core_ai.inference, json, logging, typing` | Preserve as historical reference (Deprecated) |
| `archive_engines/safe_outcome_ai/components.py` | `DEPRECATED` | 2726 | `archive_engines.hybrid_os_symbolic.symbolic_core, archive_engines.llm_os_core.memory_knowledge, intel_core_ai.inference, logging` | Preserve as historical reference (Deprecated) |
| `archive_engines/self_skeptical_engine/components.py` | `DEPRECATED` | 1099 | `intel_core_ai.inference, logging` | Preserve as historical reference (Deprecated) |

### Module `composer.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/core/composer.py` | `ACTIVE_SOURCE` | 6196 | `PIL, backend.core.refiner, base64, io` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/runtime/composer.py` | `ACTIVE_SOURCE` | 3068 | `backend.answers.fragment_engine, backend.graph.fragment_graph, backend.normalization.normalizer, logging` | Preserve for compatibility / migrate to `hyper.*` |
| `rag/composer.py` | `ACTIVE_SOURCE` | 805 | `structlog` | Preserve for compatibility / migrate to `hyper.*` |

### Module `compute_budget.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/optimization/compute_budget.py` | `ACTIVE_SOURCE` | 1878 | `backend.core.metrics, logging, psutil, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `cbe/controller/compute_budget.py` | `ACTIVE_SOURCE` | 2930 | `__future__, dataclasses, time, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `compute_optimizer.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/core/compute_optimizer.py` | `DEPRECATED` | 739 | `none` | Preserve as historical reference (Deprecated) |
| `backend/compression/compute_optimizer.py` | `ACTIVE_SOURCE` | 1657 | `hashlib, logging, time, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `config.py` (4 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/closed_loop_synthesis/config.py` | `DEPRECATED` | 911 | `os, pydantic, pydantic_settings` | Preserve as historical reference (Deprecated) |
| `archive_engines/hyper_optimized_ai/config.py` | `DEPRECATED` | 1087 | `pydantic, pydantic_settings` | Preserve as historical reference (Deprecated) |
| `archive_engines/perfect_verification_system/config.py` | `DEPRECATED` | 841 | `os, pydantic, pydantic_settings` | Preserve as historical reference (Deprecated) |
| `core/ira/shared/config.py` | `ACTIVE_SOURCE` | 8230 | `dataclasses, json, os, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `contract.py` (6 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_cco/contract.py` | `ACTIVE_SOURCE` | 14947 | `dataclasses, enum, hashlib, json` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_cel/contract/contract.py` | `ACTIVE_SOURCE` | 4261 | `abc, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_mvc_dar/contract.py` | `ACTIVE_SOURCE` | 2069 | `dataclasses, enum, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/proof/contract.py` | `EXPERIMENTAL` | 1381 | `hyper_v3.frontend.contract_parser, hyper_v3.proof.exactness, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/contract_ir/contract.py` | `ACTIVE_SOURCE` | 5909 | `__future__, dataclasses, enum, hashlib` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/contract.py` | `ACTIVE_SOURCE` | 6649 | `__future__, hyper_x.wormhole_compiler.schemas, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `contract_compiler.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_cco/contract_compiler.py` | `ACTIVE_SOURCE` | 9590 | `__future__, contract, dataclasses, enum` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v2/compiler/contract_compiler.py` | `EXPERIMENTAL` | 4846 | `dataclasses, enum, hashlib, json` | Preserve for compatibility / migrate to `hyper.*` |

### Module `contract_engine.py` (4 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/inference/contract_engine.py` | `ACTIVE_SOURCE` | 1387 | `leo_real_engine, os, sys` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/contract_engine.py` | `ACTIVE_SOURCE` | 2745 | `core_ai.architectures.kan_subsumption, core_ai.architectures.topological_shape, dfa_engine_cpp, hyper_runtime.cpu_orchestrator.cache_aware_tiling` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper100/contract_engine.py` | `EXPERIMENTAL` | 9053 | `dataclasses, enum, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `leo/contract_engine.py` | `ACTIVE_SOURCE` | 4477 | `os, sys, time` | Preserve for compatibility / migrate to `hyper.*` |

### Module `contract_engine_v1.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/routers/contract_engine_v1.py` | `ACTIVE_SOURCE` | 1645 | `fastapi, leo.contract_engine_v1, pydantic, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `leo/contract_engine_v1.py` | `ACTIVE_SOURCE` | 9882 | `dataclasses, hashlib, json, logging` | Preserve for compatibility / migrate to `hyper.*` |

### Module `contracts.py` (4 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/project_hyper/schemas/contracts.py` | `DEPRECATED` | 506 | `enum, pydantic, typing` | Preserve as historical reference (Deprecated) |
| `archive_engines/adaptive_self_correcting_system/project_hyper_final/schemas/contracts.py` | `DEPRECATED` | 595 | `enum, pydantic, typing` | Preserve as historical reference (Deprecated) |
| `archive_engines/adaptive_self_correcting_system/project_hyper_perceived/schemas/contracts.py` | `DEPRECATED` | 634 | `enum, pydantic, typing` | Preserve as historical reference (Deprecated) |
| `hyper_x/strict/contracts.py` | `ACTIVE_SOURCE` | 9431 | `__future__, dataclasses, enum, math` | Preserve for compatibility / migrate to `hyper.*` |

### Module `controller.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/project_hyper_final/fallback/controller.py` | `DEPRECATED` | 891 | `schemas.contracts` | Preserve as historical reference (Deprecated) |
| `backend/intelligence/controller.py` | `ACTIVE_SOURCE` | 1278 | `backend.intelligence.decision_engine, backend.intelligence.feedback_collector, backend.intelligence.learning_engine, backend.intelligence.policy_store` | Preserve for compatibility / migrate to `hyper.*` |

### Module `cost_model.py` (6 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_cel/scheduler/cost_model.py` | `ACTIVE_SOURCE` | 2116 | `dataclasses, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v2/search/cost_model.py` | `EXPERIMENTAL` | 3770 | `dataclasses, hyper_v2.compiler.intermediate_representation, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/learning/cost_model.py` | `EXPERIMENTAL` | 732 | `typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/search/cost_model.py` | `EXPERIMENTAL` | 3171 | `dataclasses, hyper_v3.ir.operation, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/compute_fabric/cost_model.py` | `ACTIVE_SOURCE` | 4250 | `__future__, hyper_x.compute_fabric.work_unit, math, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/cost_model.py` | `ACTIVE_SOURCE` | 5110 | `__future__, hyper_x.wormhole_compiler.schemas, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `counterfactual.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_cco/counterfactual.py` | `ACTIVE_SOURCE` | 9063 | `__future__, contract, dataclasses, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/counterfactual.py` | `ACTIVE_SOURCE` | 8900 | `__future__, hashlib, hyper_x.wormhole_compiler.schemas, numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `cpu_backend.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_v2/execution/cpu_backend.py` | `EXPERIMENTAL` | 1067 | `numpy, time, torch, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/runtime/cpu_backend.py` | `EXPERIMENTAL` | 1008 | `numpy, time, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/cpu_backend.py` | `ACTIVE_SOURCE` | 1415 | `__future__, hyper_x.hardware.fingerprint, hyper_x.wormhole_compiler.compiler_backend, numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `crystallizer.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/crystallization/crystallizer.py` | `ACTIVE_SOURCE` | 14628 | `backend.analytics.avoidance_tracker, backend.core.db_utils, faiss, hashlib` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/layer2_crystallize/crystallizer.py` | `ACTIVE_SOURCE` | 7837 | `backend.core.db_utils, logging, re, sqlite3` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/hyperdimensional/crystallizer.py` | `ACTIVE_SOURCE` | 2123 | `core, igpu_accelerator, logging, numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `dashboard.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_v3/dashboard/dashboard.py` | `EXPERIMENTAL` | 1300 | `hyper_v3.runtime.device_manager, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/dashboard.py` | `ACTIVE_SOURCE` | 10908 | `json, os, time, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `database.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/core/database.py` | `ACTIVE_SOURCE` | 9217 | `datetime, os, sqlalchemy, sqlalchemy.orm` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/nvidia_db/database.py` | `ACTIVE_SOURCE` | 8227 | `__future__, dataclasses, enum, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `delta_engine.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/answers/delta_engine.py` | `ACTIVE_SOURCE` | 1420 | `logging, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/intelligence/delta_engine.py` | `ACTIVE_SOURCE` | 4941 | `backend.rag.embedding_model, logging, numpy, re` | Preserve for compatibility / migrate to `hyper.*` |

### Module `dependency.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_v3/intelligence/dependency.py` | `EXPERIMENTAL` | 2079 | `hyper_v3.ir.graph, hyper_v3.ir.node, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/ir/dependency.py` | `EXPERIMENTAL` | 480 | `dataclasses, enum` | Preserve for compatibility / migrate to `hyper.*` |

### Module `detector.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/project_hyper_final/router/detector.py` | `DEPRECATED` | 1466 | `schemas.contracts, zlib` | Preserve as historical reference (Deprecated) |
| `archive_engines/adaptive_self_correcting_system/project_hyper_perceived/core/detector.py` | `DEPRECATED` | 1058 | `contracts, zlib` | Preserve as historical reference (Deprecated) |
| `backend/hardware/detector.py` | `ACTIVE_SOURCE` | 16412 | `__future__, coremltools, cpuinfo, dataclasses` | Preserve for compatibility / migrate to `hyper.*` |

### Module `device_manager.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_v2/execution/device_manager.py` | `EXPERIMENTAL` | 2562 | `openvino, platform, psutil, torch` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/runtime/device_manager.py` | `EXPERIMENTAL` | 2364 | `openvino, platform, psutil, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `domain_adapters.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_cco/domain_adapters.py` | `ACTIVE_SOURCE` | 5045 | `__future__, hyper_cco.contract, numpy, time` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/domain_adapters.py` | `ACTIVE_SOURCE` | 7193 | `__future__, hyper_x.wormhole_compiler.algorithm_grammar, hyper_x.wormhole_compiler.contract, hyper_x.wormhole_compiler.observable` | Preserve for compatibility / migrate to `hyper.*` |

### Module `domain_router.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/core/domain_router.py` | `DEPRECATED` | 1105 | `none` | Preserve as historical reference (Deprecated) |
| `backend/domain/domain_router.py` | `ACTIVE_SOURCE` | 1108 | `backend.domain.workspace_manager, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `elimination_engine.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper/elimination/elimination_engine.py` | `ACTIVE_SOURCE` | 1574 | `typing` | **Retain as Authoritative Source of Truth** |
| `hyper100/elimination_engine.py` | `EXPERIMENTAL` | 5093 | `dataclasses, numpy, time, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `engine.py` (19 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/project_hyper_final/rag/engine.py` | `DEPRECATED` | 826 | `typing` | Preserve as historical reference (Deprecated) |
| `archive_engines/hyper_optimized_ai/app/core/engine.py` | `DEPRECATED` | 4400 | `archive_engines.hyper_optimized_ai.app.core.filter, archive_engines.hyper_optimized_ai.app.core.gate, archive_engines.hyper_optimized_ai.app.core.output, archive_engines.hyper_optimized_ai.app.core.router` | Preserve as historical reference (Deprecated) |
| `backend/benchmarks/engine.py` | `BENCHMARK` | 8511 | `aiohttp, backend.layers.v10_beta_orchestrator, json, logging` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/vibethinker/execution/engine.py` | `ACTIVE_SOURCE` | 3743 | `abc, asyncio, backend.vibethinker.execution.registry, backend.vibethinker.execution.validator` | Preserve for compatibility / migrate to `hyper.*` |
| `chimera/engine.py` | `EXPERIMENTAL` | 5557 | `chimera.contract_classifier, chimera.hybrid_retrieval, chimera.neurosymbolic, os` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper/contracts/engine.py` | `ACTIVE_SOURCE` | 5158 | `contract_types, typing` | **Retain as Authoritative Source of Truth** |
| `hyper_ares/engine.py` | `EXPERIMENTAL` | 5073 | `dataclasses, hyper_ares.predictive_residual, hyper_ares.representation_searcher, hyper_ares.structure_detector` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_holographic_poc/cognitive_engine/engine.py` | `ACTIVE_SOURCE` | 1625 | `fastapi, llama_cpp, os, pydantic` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_mvc_dar/engine.py` | `ACTIVE_SOURCE` | 9602 | `adaptive, algorithm_discovery, complexity, contract` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/proof/engine.py` | `EXPERIMENTAL` | 2217 | `hyper_v3.frontend.contract_parser, hyper_v3.proof.certificates, hyper_v3.proof.contract, hyper_v3.proof.exactness` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/approximation/engine.py` | `ACTIVE_SOURCE` | 2465 | `__future__, dataclasses, math, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/cache/engine.py` | `ACTIVE_SOURCE` | 4113 | `__future__, dataclasses, enum, hashlib` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/communication/engine.py` | `ACTIVE_SOURCE` | 2389 | `__future__, dataclasses, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/counterfactual/engine.py` | `ACTIVE_SOURCE` | 5076 | `__future__, dataclasses, enum, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/decp/engine.py` | `ACTIVE_SOURCE` | 1432 | `comparator, manifest, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/engine.py` | `ACTIVE_SOURCE` | 8607 | `hyper_x.algorithmic_escape_search, hyper_x.contract_miner, hyper_x.falsification_loop, hyper_x.necessity_map` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/fallback/engine.py` | `ACTIVE_SOURCE` | 1157 | `numpy, time, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/falsification/engine.py` | `ACTIVE_SOURCE` | 5281 | `__future__, dataclasses, json, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/information_boundary/engine.py` | `ACTIVE_SOURCE` | 6246 | `influence_graph, numpy, time, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `engine_adapter.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `adapters/engine_adapter.py` | `ACTIVE_SOURCE` | 1954 | `logging, os, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `archive_engines/orchestration/engine_adapter.py` | `DEPRECATED` | 1942 | `logging, typing` | Preserve as historical reference (Deprecated) |

### Module `error_budget.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `contracts/error_budget.py` | `ACTIVE_SOURCE` | 3147 | `enum, numpy, time, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_mvc_dar/error_budget.py` | `ACTIVE_SOURCE` | 1263 | `typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `event_vision.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/engine_hv/vision/event_vision.py` | `DEPRECATED` | 1586 | `logging, numpy, typing` | Preserve as historical reference (Deprecated) |
| `archive_engines/orchestration/event_vision.py` | `DEPRECATED` | 2882 | `logging, numpy, time, typing` | Preserve as historical reference (Deprecated) |

### Module `exact_cache.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_cco/exact_cache.py` | `ACTIVE_SOURCE` | 9830 | `dataclasses, enum, hashlib, json` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_cel/reuse/exact_cache.py` | `ACTIVE_SOURCE` | 2955 | `hashlib, numpy, time, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `execution.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/llm_os_core/execution.py` | `DEPRECATED` | 4700 | `archive_engines.llm_os_core.memory_knowledge, intel_core_ai.inference, logging, typing` | Preserve as historical reference (Deprecated) |
| `execution/execution.py` | `ACTIVE_SOURCE` | 244 | `core.inference` | Preserve for compatibility / migrate to `hyper.*` |

### Module `extract_signals.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/reflect/scripts/extract_signals.py` | `ACTIVE_SOURCE` | 12630 | `argparse, json, os, pathlib` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/reflection/claude-reflect-system-master/reflect/scripts/extract_signals.py` | `ACTIVE_SOURCE` | 12630 | `argparse, json, os, pathlib` | Preserve for compatibility / migrate to `hyper.*` |

### Module `fallback_ladder.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_mvc_dar/fallback_ladder.py` | `ACTIVE_SOURCE` | 2363 | `enum, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v2/strategies/fallback_ladder.py` | `EXPERIMENTAL` | 3336 | `enum, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/mvc/fallback_ladder.py` | `EXPERIMENTAL` | 3934 | `enum, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `fusion.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper/compiler/fusion.py` | `ACTIVE_SOURCE` | 1491 | `numpy, time, typing` | **Retain as Authoritative Source of Truth** |
| `hyper_v3/transforms/fusion.py` | `EXPERIMENTAL` | 827 | `numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `governor.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/routers/governor.py` | `ACTIVE_SOURCE` | 6657 | `ctypes, fastapi, logging, os` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/governor.py` | `ACTIVE_SOURCE` | 4505 | `gc, logging, os, psutil` | Preserve for compatibility / migrate to `hyper.*` |

### Module `graph.py` (4 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/data_efficiency/graph.py` | `ACTIVE_SOURCE` | 1545 | `logging, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper/workload/graph.py` | `ACTIVE_SOURCE` | 955 | `dataclasses, typing` | **Retain as Authoritative Source of Truth** |
| `hyper_v3/ir/graph.py` | `EXPERIMENTAL` | 7112 | `collections, dataclasses, hashlib, hyper_v3.ir.dependency` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/transforms/graph.py` | `EXPERIMENTAL` | 570 | `hyper_v3.ir.graph, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `graph_builder.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/graph/graph_builder.py` | `ACTIVE_SOURCE` | 2441 | `backend.graph.graph_store, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v2/compiler/graph_builder.py` | `EXPERIMENTAL` | 4971 | `hyper_v2.compiler.contract_compiler, hyper_v2.compiler.intermediate_representation, math, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `hardness.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/core/hardness.py` | `DEPRECATED` | 1319 | `enum, zlib` | Preserve as historical reference (Deprecated) |
| `archive_engines/adaptive_self_correcting_system/project_hyper/router/hardness.py` | `DEPRECATED` | 1292 | `schemas.contracts, zlib` | Preserve as historical reference (Deprecated) |

### Module `hardware_model.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_v3/learning/hardware_model.py` | `EXPERIMENTAL` | 1389 | `hyper_v3.learning.profiler, hyper_v3.runtime.device_manager, json, os` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/hardware_model.py` | `ACTIVE_SOURCE` | 4760 | `__future__, dataclasses, hyper_x.hardware.fingerprint, hyper_x.wormhole_compiler.schemas` | Preserve for compatibility / migrate to `hyper.*` |

### Module `heterogeneous.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/compute/heterogeneous.py` | `ACTIVE_SOURCE` | 3565 | `logging, numpy, onnxruntime, os` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/fabric/heterogeneous.py` | `ACTIVE_SOURCE` | 4187 | `__future__, dataclasses, enum, numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `heterogeneous_fabric.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `core_ai/breakthrough/heterogeneous_fabric.py` | `ACTIVE_SOURCE` | 3999 | `collections, numpy, pyopencl, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_mvc_dar/heterogeneous_fabric.py` | `ACTIVE_SOURCE` | 2112 | `numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/runtime/heterogeneous_fabric.py` | `EXPERIMENTAL` | 2300 | `hyper_v3.runtime.cpu_backend, hyper_v3.runtime.device_manager, hyper_v3.runtime.hybrid_backend, hyper_v3.runtime.igpu_backend` | Preserve for compatibility / migrate to `hyper.*` |

### Module `heterogeneous_orchestrator.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `core_ai/heterogeneous_orchestrator.py` | `ACTIVE_SOURCE` | 9779 | `concurrent.futures, dynamic_morpher, hyper_speculative, logging` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/heterogeneous_orchestrator.py` | `ACTIVE_SOURCE` | 5420 | `logging, numpy, openvino, time` | Preserve for compatibility / migrate to `hyper.*` |

### Module `heterogeneous_scheduler.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper/scheduler/heterogeneous_scheduler.py` | `ACTIVE_SOURCE` | 1925 | `numpy, time, typing` | **Retain as Authoritative Source of Truth** |
| `hyper100/heterogeneous_scheduler.py` | `EXPERIMENTAL` | 4704 | `dataclasses, enum, numpy, os` | Preserve for compatibility / migrate to `hyper.*` |

### Module `hierarchical_rag.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/project_hyper/rag/hierarchical_rag.py` | `DEPRECATED` | 755 | `typing` | Preserve as historical reference (Deprecated) |
| `phoenix/hierarchical_rag.py` | `EXPERIMENTAL` | 2303 | `faiss, logging, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `holdout.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_v3/benchmark/holdout.py` | `BENCHMARK` | 1583 | `hyper_v3.frontend.contract_parser, hyper_v3.verification.independent_verifier, hyper_v3.workloads.adversarial_suite, hyper_v3.workloads.holdout_suite` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/verification/holdout.py` | `ACTIVE_SOURCE` | 2103 | `numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/holdout.py` | `ACTIVE_SOURCE` | 5876 | `__future__, dataclasses, hashlib, hyper_x.wormhole_compiler.schemas` | Preserve for compatibility / migrate to `hyper.*` |

### Module `hybrid_backend.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_v2/execution/hybrid_backend.py` | `EXPERIMENTAL` | 1646 | `hyper_v2.execution.cpu_backend, hyper_v2.execution.igpu_backend, hyper_v2.reformulation.sparse_reformulation, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/runtime/hybrid_backend.py` | `EXPERIMENTAL` | 1033 | `hyper_v3.runtime.cpu_backend, hyper_v3.runtime.igpu_backend, numpy, time` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/hybrid_backend.py` | `ACTIVE_SOURCE` | 2705 | `__future__, hyper_x.wormhole_compiler.compiler_backend, hyper_x.wormhole_compiler.cpu_backend, hyper_x.wormhole_compiler.igpu_backend` | Preserve for compatibility / migrate to `hyper.*` |

### Module `hybrid_retrieval.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/retrieval/hybrid_retrieval.py` | `ACTIVE_SOURCE` | 8963 | `backend.cache.semantic_cache, backend.core.db_utils, docx, hashlib` | Preserve for compatibility / migrate to `hyper.*` |
| `chimera/hybrid_retrieval.py` | `EXPERIMENTAL` | 5988 | `faiss, json, numpy, os` | Preserve for compatibility / migrate to `hyper.*` |

### Module `hyper3_cli.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_v3/cli/hyper3_cli.py` | `EXPERIMENTAL` | 6412 | `argparse, hyper_v3.audit.report_generator, hyper_v3.benchmark.holdout, hyper_v3.benchmark.runner` | Preserve for compatibility / migrate to `hyper.*` |
| `scripts/hyper3_cli.py` | `ACTIVE_SOURCE` | 296 | `hyper_v3.cli.hyper3_cli, os, sys` | Preserve for compatibility / migrate to `hyper.*` |

### Module `hyper_cli.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `cli/hyper_cli.py` | `ACTIVE_SOURCE` | 19871 | `argparse, hyper_mvc_dar, hyper_mvc_dar.ucsp.benchmark_ucsp, json` | Preserve for compatibility / migrate to `hyper.*` |
| `scripts/hyper_cli.py` | `ACTIVE_SOURCE` | 6136 | `algorithm_discovery.complexity_transformer, algorithm_discovery.generator, argparse, hyper_v3.audit.auto_audit` | Preserve for compatibility / migrate to `hyper.*` |

### Module `hyper_engine.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `HYPER_v6_BREAKTHROUGH/hyper_engine.py` | `ACTIVE_SOURCE` | 10048 | `argparse, cache_engine, contract_analyzer, core_ai.alchemy_engine` | Preserve for compatibility / migrate to `hyper.*` |
| `archive_engines/orchestration/hyper_engine.py` | `DEPRECATED` | 2188 | `numba, numpy, time` | Preserve as historical reference (Deprecated) |

### Module `igpu_accelerator.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `core_ai/hyperdimensional/igpu_accelerator.py` | `ACTIVE_SOURCE` | 4178 | `colibri_bridge, logging, numpy, pyopencl` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/igpu_accelerator.py` | `ACTIVE_SOURCE` | 12016 | `llama_cpp, logging, numpy, openvino.runtime` | Preserve for compatibility / migrate to `hyper.*` |

### Module `igpu_backend.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_v2/execution/igpu_backend.py` | `EXPERIMENTAL` | 1290 | `numpy, openvino, time, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/runtime/igpu_backend.py` | `EXPERIMENTAL` | 1057 | `numpy, openvino, time, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/igpu_backend.py` | `ACTIVE_SOURCE` | 2153 | `__future__, hyper_x.hardware.fingerprint, hyper_x.wormhole_compiler.compiler_backend, numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `independent_verifier.py` (6 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `core_ai/independent_verifier.py` | `ACTIVE_SOURCE` | 7072 | `core_ai.avx2_fast_matmul, core_ai.causal_physics_engine, core_ai.diff_logic_engine, core_ai.mamba_ssm_engine` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/verification/independent_verifier.py` | `ACTIVE_SOURCE` | 3959 | `dataclasses, numpy, time, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_mvc_dar/independent_verifier.py` | `ACTIVE_SOURCE` | 2712 | `numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v2/verification/independent_verifier.py` | `EXPERIMENTAL` | 4232 | `dataclasses, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/verification/independent_verifier.py` | `EXPERIMENTAL` | 3474 | `dataclasses, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/independent_verifier.py` | `ACTIVE_SOURCE` | 11004 | `dataclasses, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `inference.py` (6 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/project_hyper/models/inference.py` | `DEPRECATED` | 861 | `asyncio, typing` | Preserve as historical reference (Deprecated) |
| `archive_engines/high_perf_intel_ai/inference.py` | `DEPRECATED` | 2020 | `llama_cpp, logging, os, typing` | Preserve as historical reference (Deprecated) |
| `archive_engines/vulkan_intel_ai/inference.py` | `DEPRECATED` | 2194 | `llama_cpp, logging, os, typing` | Preserve as historical reference (Deprecated) |
| `core/inference.py` | `ACTIVE_SOURCE` | 264 | `none` | Preserve for compatibility / migrate to `hyper.*` |
| `intel_core_ai/inference.py` | `ACTIVE_SOURCE` | 2100 | `llama_cpp, logging, os, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `rag/inference.py` | `ACTIVE_SOURCE` | 2562 | `llama_cpp, os, structlog` | Preserve for compatibility / migrate to `hyper.*` |

### Module `input_logic.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `core/input_logic.py` | `ACTIVE_SOURCE` | 174 | `none` | Preserve for compatibility / migrate to `hyper.*` |
| `intel_core_ai/input_logic.py` | `ACTIVE_SOURCE` | 1356 | `logging, pydantic, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `intent.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/hybrid/intent.py` | `ACTIVE_SOURCE` | 6071 | `logging, numpy, os, re` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/vibethinker/router/intent.py` | `ACTIVE_SOURCE` | 519 | `none` | Preserve for compatibility / migrate to `hyper.*` |

### Module `ir.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_mvc_dar/ir.py` | `ACTIVE_SOURCE` | 4331 | `dataclasses, enum, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/compiler/ir.py` | `ACTIVE_SOURCE` | 3939 | `__future__, dataclasses, enum, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/ir.py` | `ACTIVE_SOURCE` | 3403 | `__future__, dataclasses, json, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `irreducibility.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_mvc_dar/irreducibility.py` | `ACTIVE_SOURCE` | 1678 | `dataclasses, json, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/audit/irreducibility.py` | `EXPERIMENTAL` | 3572 | `typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `jit_compiler.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `core_ai/jit_compiler.py` | `ACTIVE_SOURCE` | 1717 | `logging, psutil, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_runtime/dynamic_kernel/jit_compiler.py` | `ACTIVE_SOURCE` | 855 | `none` | Preserve for compatibility / migrate to `hyper.*` |

### Module `kernel.py` (12 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_compute_router/kernel.py` | `DEPRECATED` | 2436 | `archive_engines.adaptive_compute_router.router, archive_engines.vulkan_intel_ai.cache, intel_core_ai.inference, logging` | Preserve as historical reference (Deprecated) |
| `archive_engines/boundary_perfect_ai/kernel.py` | `DEPRECATED` | 2160 | `archive_engines.boundary_perfect_ai.intent_handler, archive_engines.boundary_perfect_ai.reasoning_engine, archive_engines.hybrid_os_symbolic.symbolic_core, archive_engines.outcome_driven_ai.classifier_critic` | Preserve as historical reference (Deprecated) |
| `archive_engines/controlled_ai_pipeline/kernel.py` | `DEPRECATED` | 2835 | `archive_engines.controlled_ai_pipeline.scorer, archive_engines.high_perf_intel_ai.inference, archive_engines.hybrid_os_symbolic.symbolic_core, archive_engines.llm_os_core.memory_knowledge` | Preserve as historical reference (Deprecated) |
| `archive_engines/high_accuracy_engine/kernel.py` | `DEPRECATED` | 2707 | `archive_engines.high_accuracy_engine.components, archive_engines.hybrid_os_symbolic.symbolic_core, archive_engines.llm_os_core.memory_knowledge, intel_core_ai.inference` | Preserve as historical reference (Deprecated) |
| `archive_engines/high_perf_intel_ai/kernel.py` | `DEPRECATED` | 2594 | `archive_engines.high_perf_intel_ai.inference, archive_engines.hybrid_os_symbolic.symbolic_core, archive_engines.llm_os_core.memory_knowledge, asyncio` | Preserve as historical reference (Deprecated) |
| `archive_engines/hybrid_os_symbolic/kernel.py` | `DEPRECATED` | 1926 | `archive_engines.hybrid_os_symbolic.router, archive_engines.hybrid_os_symbolic.symbolic_core, archive_engines.llm_os_core.memory_knowledge, intel_core_ai.inference` | Preserve as historical reference (Deprecated) |
| `archive_engines/hyper_core_ai/kernel.py` | `DEPRECATED` | 2165 | `archive_engines.hyper_core_ai.memory, intel_core_ai.inference, json, logging` | Preserve as historical reference (Deprecated) |
| `archive_engines/outcome_driven_ai/kernel.py` | `DEPRECATED` | 2269 | `archive_engines.hybrid_os_symbolic.symbolic_core, archive_engines.outcome_driven_ai.classifier_critic, intel_core_ai.inference, logging` | Preserve as historical reference (Deprecated) |
| `archive_engines/safe_outcome_ai/kernel.py` | `DEPRECATED` | 2612 | `archive_engines.hybrid_os_symbolic.symbolic_core, archive_engines.llm_os_core.memory_knowledge, archive_engines.outcome_driven_ai.classifier_critic, archive_engines.safe_outcome_ai.components` | Preserve as historical reference (Deprecated) |
| `archive_engines/self_skeptical_engine/kernel.py` | `DEPRECATED` | 3029 | `archive_engines.high_accuracy_engine.components, archive_engines.hybrid_os_symbolic.symbolic_core, archive_engines.llm_os_core.memory_knowledge, archive_engines.self_skeptical_engine.components` | Preserve as historical reference (Deprecated) |
| `archive_engines/verified_outcome_ai/kernel.py` | `DEPRECATED` | 4420 | `asyncio, intel_core_ai.inference, json, logging` | Preserve as historical reference (Deprecated) |
| `archive_engines/vulkan_intel_ai/kernel.py` | `DEPRECATED` | 2436 | `archive_engines.hybrid_os_symbolic.symbolic_core, archive_engines.llm_os_core.memory_knowledge, archive_engines.vulkan_intel_ai.inference, json` | Preserve as historical reference (Deprecated) |

### Module `knowledge.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/hybrid_intel_ai/knowledge.py` | `DEPRECATED` | 1450 | `intel_core_ai.knowledge, logging, typing` | Preserve as historical reference (Deprecated) |
| `intel_core_ai/knowledge.py` | `ACTIVE_SOURCE` | 1976 | `faiss, logging, numpy, sentence_transformers` | Preserve for compatibility / migrate to `hyper.*` |
| `memory/knowledge.py` | `ACTIVE_SOURCE` | 523 | `core_ai.fabric.topological_hypergraph` | Preserve for compatibility / migrate to `hyper.*` |

### Module `knowledge_base.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `core/ira/nsf/knowledge_base.py` | `ACTIVE_SOURCE` | 8142 | `core.ira.nsf.safe_calculator, core.ira.shared.text, json, os` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/knowledge/knowledge_base.py` | `ACTIVE_SOURCE` | 2183 | `typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/knowledge_base.py` | `ACTIVE_SOURCE` | 4393 | `__future__, dataclasses, hyper_x.wormhole_compiler.schemas, json` | Preserve for compatibility / migrate to `hyper.*` |

### Module `knowledge_graph.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/core/knowledge_graph.py` | `ACTIVE_SOURCE` | 12944 | `backend.core.db_utils, collections, hashlib, json` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/knowledge/knowledge_graph.py` | `ACTIVE_SOURCE` | 5562 | `collections, logging, time, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_runtime/symbolic_hybrid/knowledge_graph.py` | `ACTIVE_SOURCE` | 1624 | `logging, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `knowledge_layer.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/core/knowledge_layer.py` | `DEPRECATED` | 696 | `typing` | Preserve as historical reference (Deprecated) |
| `core_ai/knowledge_layer.py` | `ACTIVE_SOURCE` | 1962 | `asyncio, chromadb, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `kv_cache.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/inference/kv_cache.py` | `ACTIVE_SOURCE` | 3947 | `backend.intelligence.router, hashlib, json, logging` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_runtime/kv_persistence/kv_cache.py` | `ACTIVE_SOURCE` | 1814 | `json, os` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/ai/kv_cache.py` | `ACTIVE_SOURCE` | 2085 | `__future__, hashlib, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `kv_compression.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_runtime/kv_persistence/kv_compression.py` | `ACTIVE_SOURCE` | 846 | `numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `phoenix/kv_compression.py` | `EXPERIMENTAL` | 8308 | `logging, torch, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `l2_semantic_cache.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/layers/l2_semantic_cache.py` | `ACTIVE_SOURCE` | 1263 | `backend.cache.semantic_cache, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `project_hyper/layers/l2_semantic_cache.py` | `ACTIVE_SOURCE` | 1553 | `faiss, sentence_transformers, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `latency_controller.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/core/latency_controller.py` | `ACTIVE_SOURCE` | 3077 | `logging, psutil, time, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `cbe/controller/latency_controller.py` | `ACTIVE_SOURCE` | 3661 | `__future__, dataclasses, numpy, time` | Preserve for compatibility / migrate to `hyper.*` |

### Module `learning_ledger.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/reflect/scripts/learning_ledger.py` | `ACTIVE_SOURCE` | 12934 | `argparse, datetime, hashlib, json` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/reflection/claude-reflect-system-master/reflect/scripts/learning_ledger.py` | `ACTIVE_SOURCE` | 12934 | `argparse, datetime, hashlib, json` | Preserve for compatibility / migrate to `hyper.*` |

### Module `ledger.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper/telemetry/ledger.py` | `ACTIVE_SOURCE` | 828 | `json, time, typing` | **Retain as Authoritative Source of Truth** |
| `hyper_v3/telemetry/ledger.py` | `EXPERIMENTAL` | 2552 | `dataclasses, json, os, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/evidence/ledger.py` | `ACTIVE_SOURCE` | 3196 | `__future__, hyper_x.certificates.certificate, json, os` | Preserve for compatibility / migrate to `hyper.*` |

### Module `leo_engine.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `core_ai/leo_engine.py` | `ACTIVE_SOURCE` | 9892 | `attention, bitnet_engine, moe_architecture, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `leo_engine.py` | `ACTIVE_SOURCE` | 13422 | `backend.reflect.leo_reflect_service, gc, json, numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `logging.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/core/logging.py` | `ACTIVE_SOURCE` | 675 | `logging, structlog, sys` | Preserve for compatibility / migrate to `hyper.*` |
| `core/ira/shared/logging.py` | `ACTIVE_SOURCE` | 3310 | `datetime, json, logging, os` | Preserve for compatibility / migrate to `hyper.*` |

### Module `low_rank.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_mvc_dar/low_rank.py` | `ACTIVE_SOURCE` | 1868 | `numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v2/reformulation/low_rank.py` | `EXPERIMENTAL` | 2512 | `numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `low_rank_engine.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper/low_rank/low_rank_engine.py` | `ACTIVE_SOURCE` | 2550 | `numpy, time, typing` | **Retain as Authoritative Source of Truth** |
| `hyper100/low_rank_engine.py` | `EXPERIMENTAL` | 3897 | `dataclasses, numpy, time, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_cco/low_rank_engine.py` | `ACTIVE_SOURCE` | 7180 | `dataclasses, enum, numpy, time` | Preserve for compatibility / migrate to `hyper.*` |

### Module `main.py` (9 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/project_hyper/api/main.py` | `DEPRECATED` | 1102 | `fastapi, fastapi.responses, metrics.telemetry, orchestrator` | Preserve as historical reference (Deprecated) |
| `archive_engines/adaptive_self_correcting_system/project_hyper_final/api/main.py` | `DEPRECATED` | 826 | `backend.orchestrator, fastapi, fastapi.responses, metrics.telemetry` | Preserve as historical reference (Deprecated) |
| `archive_engines/adaptive_self_correcting_system/project_hyper_perceived/api/main.py` | `DEPRECATED` | 517 | `core.router, fastapi, schemas.contracts, uvicorn` | Preserve as historical reference (Deprecated) |
| `archive_engines/closed_loop_synthesis/main.py` | `DEPRECATED` | 3309 | `archive_engines.closed_loop_synthesis.config, archive_engines.closed_loop_synthesis.core.analyzer, archive_engines.closed_loop_synthesis.core.cache, archive_engines.closed_loop_synthesis.core.proposer` | Preserve as historical reference (Deprecated) |
| `archive_engines/hybrid_ai_system/main.py` | `DEPRECATED` | 2784 | `archive_engines.hybrid_ai_system.core.closed_logic, archive_engines.hybrid_ai_system.core.open_logic, archive_engines.hybrid_ai_system.core.router, archive_engines.hybrid_ai_system.services.model_manager` | Preserve as historical reference (Deprecated) |
| `archive_engines/hyper_optimized_ai/app/main.py` | `DEPRECATED` | 2357 | `archive_engines.hyper_optimized_ai.app.core.engine, asyncio, fastapi, fastapi.responses` | Preserve as historical reference (Deprecated) |
| `archive_engines/hyper_optimized_ai/main.py` | `DEPRECATED` | 294 | `os, uvicorn` | Preserve as historical reference (Deprecated) |
| `backend/main.py` | `ACTIVE_SOURCE` | 5981 | `backend.api_v2_bypass, backend.core.database, backend.core.health, backend.core.memory_system` | Preserve for compatibility / migrate to `hyper.*` |
| `project_hyper/main.py` | `ACTIVE_SOURCE` | 2227 | `project_hyper.cache, project_hyper.compute, project_hyper.rag, project_hyper.reasoning` | Preserve for compatibility / migrate to `hyper.*` |

### Module `memory.py` (6 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/hyper_core_ai/memory.py` | `DEPRECATED` | 1344 | `archive_engines.hybrid_intel_ai.knowledge, logging, typing` | Preserve as historical reference (Deprecated) |
| `archive_engines/llm_os_intel/memory.py` | `DEPRECATED` | 1401 | `archive_engines.hybrid_intel_ai.knowledge, logging, typing` | Preserve as historical reference (Deprecated) |
| `backend/core/memory.py` | `ACTIVE_SOURCE` | 4153 | `backend.core.db_utils, backend.core.middleware, datetime, json` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/routers/memory.py` | `ACTIVE_SOURCE` | 1574 | `backend.core.db_utils, backend.core.memory_system, fastapi, pydantic` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/transforms/memory.py` | `EXPERIMENTAL` | 861 | `numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `memory/memory.py` | `ACTIVE_SOURCE` | 929 | `core.paradigm_bypass.layer3_virtual_memory, core_ai.fabric.topological_hypergraph, numpy, os` | Preserve for compatibility / migrate to `hyper.*` |

### Module `memory_engine.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper/memory/memory_engine.py` | `ACTIVE_SOURCE` | 1392 | `numpy, typing` | **Retain as Authoritative Source of Truth** |
| `hyper_mvc_dar/memory_engine.py` | `ACTIVE_SOURCE` | 1806 | `numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `memory_manager.py` (4 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/core/memory_manager.py` | `DEPRECATED` | 1463 | `models.schemas, typing` | Preserve as historical reference (Deprecated) |
| `core_ai/memory_manager.py` | `ACTIVE_SOURCE` | 5320 | `gc, logging, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/memory/memory_manager.py` | `ACTIVE_SOURCE` | 3340 | `__future__, dataclasses, gc, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `phoenix/memory_manager.py` | `EXPERIMENTAL` | 2524 | `logging, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `meta_learning.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/reflect/scripts/meta_learning.py` | `ACTIVE_SOURCE` | 15193 | `collections, datetime, json, os` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/reflection/claude-reflect-system-master/reflect/scripts/meta_learning.py` | `ACTIVE_SOURCE` | 15193 | `collections, datetime, json, os` | Preserve for compatibility / migrate to `hyper.*` |

### Module `metrics.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/analytics/metrics.py` | `ACTIVE_SOURCE` | 4193 | `json, logging, os, time` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/core/metrics.py` | `ACTIVE_SOURCE` | 5447 | `prometheus_client` | Preserve for compatibility / migrate to `hyper.*` |
| `core/ira/shared/metrics.py` | `ACTIVE_SOURCE` | 6714 | `collections, dataclasses, json, os` | Preserve for compatibility / migrate to `hyper.*` |

### Module `micro_compute.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/intelligence/micro_compute.py` | `ACTIVE_SOURCE` | 1524 | `backend.models.llm_loader, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/optimization/micro_compute.py` | `ACTIVE_SOURCE` | 2210 | `asyncio, backend.optimization.compute_budget, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `model_manager.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/hybrid_ai_system/services/model_manager.py` | `DEPRECATED` | 916 | `llama_cpp, os` | Preserve as historical reference (Deprecated) |
| `backend/core/model_manager.py` | `ACTIVE_SOURCE` | 5470 | `asyncio, os, psutil, rag.inference` | Preserve for compatibility / migrate to `hyper.*` |

### Module `necessity.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_mvc_dar/necessity.py` | `ACTIVE_SOURCE` | 2498 | `contract, enum, ir, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/intelligence/necessity.py` | `EXPERIMENTAL` | 4723 | `dataclasses, hyper_v3.frontend.contract_parser, hyper_v3.ir.operation, numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `necessity_analyzer.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper/necessity/necessity_analyzer.py` | `ACTIVE_SOURCE` | 2290 | `dataclasses, enum, hyper.ir.workload_ir, typing` | **Retain as Authoritative Source of Truth** |
| `hyper_v2/analysis/necessity_analyzer.py` | `EXPERIMENTAL` | 7591 | `dataclasses, hyper_v2.compiler.contract_compiler, hyper_v2.compiler.intermediate_representation, numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `numerical.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_v3/proof/numerical.py` | `EXPERIMENTAL` | 1563 | `numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/verification/numerical.py` | `ACTIVE_SOURCE` | 4511 | `hashlib, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `optimizer.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_cco/optimizer.py` | `ACTIVE_SOURCE` | 14971 | `algebraic_engine, contract, dataclasses, exact_cache` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/compiler/optimizer.py` | `ACTIVE_SOURCE` | 3442 | `__future__, hyper_x.compiler.ir, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `orchestrator.py` (12 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/core/orchestrator.py` | `DEPRECATED` | 2285 | `cache_rag, models.schemas, models_router, numpy` | Preserve as historical reference (Deprecated) |
| `archive_engines/adaptive_self_correcting_system/orchestrator.py` | `DEPRECATED` | 3323 | `core.engines, core.resources, models.schemas` | Preserve as historical reference (Deprecated) |
| `archive_engines/adaptive_self_correcting_system/project_hyper/orchestrator.py` | `DEPRECATED` | 1630 | `cache.semantic_cache, models.inference, numpy, rag.hierarchical_rag` | Preserve as historical reference (Deprecated) |
| `archive_engines/adaptive_self_correcting_system/project_hyper_final/backend/orchestrator.py` | `DEPRECATED` | 1781 | `cache.fuzzy, fallback.controller, models.quantized, numpy` | Preserve as historical reference (Deprecated) |
| `backend/core/orchestrator.py` | `ACTIVE_SOURCE` | 12496 | `answers.fragment_engine, answers.semantic_canonical, asyncio, backend.analytics.metrics` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/hybrid/orchestrator.py` | `ACTIVE_SOURCE` | 6154 | `backend.hybrid.cache, backend.hybrid.intent, backend.hybrid.rag, backend.hybrid.reasoning` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/os/orchestrator.py` | `ACTIVE_SOURCE` | 6494 | `aiohttp, asyncio, backend.compute.heterogeneous, backend.execution.parallel_framework` | Preserve for compatibility / migrate to `hyper.*` |
| `core/paradigm_bypass/orchestrator.py` | `ACTIVE_SOURCE` | 3326 | `json, layer1_binary_resonance, layer2_anomaly_driven, layer3_virtual_memory` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v2/api/orchestrator.py` | `EXPERIMENTAL` | 2502 | `hyper_v2.analysis.necessity_analyzer, hyper_v2.compiler.contract_compiler, hyper_v2.compiler.graph_builder, hyper_v2.compiler.graph_optimizer` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/orchestrator/orchestrator.py` | `ACTIVE_SOURCE` | 4880 | `__future__, dataclasses, enum, os` | Preserve for compatibility / migrate to `hyper.*` |
| `project_hyper/core/orchestrator.py` | `ACTIVE_SOURCE` | 4609 | `asyncio, project_hyper.layers.l0_intelligence, project_hyper.layers.l10_gpu_fallback, project_hyper.layers.l11_learning_loop` | Preserve for compatibility / migrate to `hyper.*` |
| `universal_compute_router/orchestrator.py` | `ACTIVE_SOURCE` | 3675 | `intel_core_ai.inference, logging, time, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `parser.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/vibethinker/ir/parser.py` | `ACTIVE_SOURCE` | 884 | `backend.vibethinker.ir.models, json` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/contract_ir/parser.py` | `ACTIVE_SOURCE` | 4570 | `contract, numpy, typing, workload_classifier` | Preserve for compatibility / migrate to `hyper.*` |

### Module `performance_monitor.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `core/quantum/heterogeneous/performance_monitor.py` | `ACTIVE_SOURCE` | 1542 | `time, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/performance_monitor.py` | `ACTIVE_SOURCE` | 8172 | `collections, dataclasses, json, logging` | Preserve for compatibility / migrate to `hyper.*` |

### Module `pipeline.py` (4 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/layer18_neural_blender/pipeline.py` | `ACTIVE_SOURCE` | 2821 | `backend.layer18_neural_blender.controlnet_renderer, backend.layer18_neural_blender.embree_oidn_optimizer, backend.layer18_neural_blender.fsr_vulkan_upscaler, backend.layer18_neural_blender.gaussian_splat_converter` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/runtime/pipeline.py` | `EXPERIMENTAL` | 641 | `time, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/graphics/pipeline.py` | `ACTIVE_SOURCE` | 3733 | `__future__, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/pipeline.py` | `ACTIVE_SOURCE` | 14505 | `__future__, argparse, hyper_x.certificates.certificate, hyper_x.compute_fabric.fabric` | Preserve for compatibility / migrate to `hyper.*` |

### Module `precision_engine.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper/precision/precision_engine.py` | `ACTIVE_SOURCE` | 2092 | `numpy, typing` | **Retain as Authoritative Source of Truth** |
| `hyper100/precision_engine.py` | `EXPERIMENTAL` | 5171 | `contract_engine, dataclasses, enum, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_cco/precision_engine.py` | `ACTIVE_SOURCE` | 9485 | `dataclasses, enum, numpy, time` | Preserve for compatibility / migrate to `hyper.*` |

### Module `prediction_engine.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper/prediction/prediction_engine.py` | `ACTIVE_SOURCE` | 1223 | `numpy, typing` | **Retain as Authoritative Source of Truth** |
| `hyper100/prediction_engine.py` | `EXPERIMENTAL` | 5012 | `contract_engine, dataclasses, enum, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/prediction/prediction_engine.py` | `ACTIVE_SOURCE` | 3962 | `__future__, dataclasses, numpy, time` | Preserve for compatibility / migrate to `hyper.*` |

### Module `predictive_engine.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/execution/predictive_engine.py` | `ACTIVE_SOURCE` | 2278 | `logging, threading, time, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `phoenix/predictive_engine.py` | `EXPERIMENTAL` | 3695 | `asyncio, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `predictive_reality.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `core_ai/fabric/predictive_reality.py` | `ACTIVE_SOURCE` | 2006 | `hashlib, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `predictors/predictive_reality.py` | `ACTIVE_SOURCE` | 2009 | `__future__, logging, random, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `predictor.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/background/predictor.py` | `ACTIVE_SOURCE` | 1928 | `asyncio, backend.models.llm_loader, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/predictive/predictor.py` | `ACTIVE_SOURCE` | 3625 | `asyncio, backend.background.compute_engine, backend.normalization.normalizer, logging` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_cel/prediction/predictor.py` | `ACTIVE_SOURCE` | 3255 | `core_ai.alchemy_kan_ffn, numpy, time, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `prefetch.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/routers/prefetch.py` | `ACTIVE_SOURCE` | 4308 | `__future__, backend.crystallization.crystallizer, backend.inference.speculative_decoder, fastapi` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/memory/prefetch.py` | `EXPERIMENTAL` | 690 | `typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `present_review.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/reflect/scripts/present_review.py` | `ACTIVE_SOURCE` | 10116 | `difflib, json, meta_learning, pathlib` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/reflection/claude-reflect-system-master/reflect/scripts/present_review.py` | `ACTIVE_SOURCE` | 10116 | `difflib, json, meta_learning, pathlib` | Preserve for compatibility / migrate to `hyper.*` |

### Module `probabilistic.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/approximation/probabilistic.py` | `DEPRECATED` | 1226 | `logging, zlib` | Preserve as historical reference (Deprecated) |
| `archive_engines/engine_hv/advanced/probabilistic.py` | `DEPRECATED` | 2816 | `hashlib, logging, typing` | Preserve as historical reference (Deprecated) |
| `backend/data_efficiency/probabilistic.py` | `ACTIVE_SOURCE` | 1569 | `asyncio, hashlib, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `profiler.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_runtime/telemetry/profiler.py` | `ACTIVE_SOURCE` | 475 | `cProfile, io, pstats` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/learning/profiler.py` | `EXPERIMENTAL` | 1215 | `numpy, time, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `promote_learning.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/reflect/scripts/promote_learning.py` | `ACTIVE_SOURCE` | 8171 | `argparse, datetime, json, learning_ledger` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/reflection/claude-reflect-system-master/reflect/scripts/promote_learning.py` | `ACTIVE_SOURCE` | 8171 | `argparse, datetime, json, learning_ledger` | Preserve for compatibility / migrate to `hyper.*` |

### Module `proposer.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/closed_loop_synthesis/core/proposer.py` | `DEPRECATED` | 2825 | `archive_engines.closed_loop_synthesis.config, llama_cpp, logging, os` | Preserve as historical reference (Deprecated) |
| `archive_engines/perfect_verification_system/core/proposer.py` | `DEPRECATED` | 982 | `llama_cpp, os, typing` | Preserve as historical reference (Deprecated) |

### Module `rag.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/hybrid/rag.py` | `ACTIVE_SOURCE` | 2367 | `chromadb, httpx, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/intelligence/rag.py` | `ACTIVE_SOURCE` | 11628 | `backend.core.middleware, backend.hybrid.intent, backend.intelligence.reranker, backend.security.prompt_guard` | Preserve for compatibility / migrate to `hyper.*` |
| `project_hyper/rag.py` | `ACTIVE_SOURCE` | 650 | `chromadb` | Preserve for compatibility / migrate to `hyper.*` |

### Module `reasoning.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/hybrid/reasoning.py` | `ACTIVE_SOURCE` | 2274 | `asyncio, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/intelligence/reasoning.py` | `ACTIVE_SOURCE` | 8951 | `backend.core.memory, backend.core.metrics, backend.core.model_manager, backend.core.tools` | Preserve for compatibility / migrate to `hyper.*` |
| `project_hyper/reasoning.py` | `ACTIVE_SOURCE` | 1008 | `none` | Preserve for compatibility / migrate to `hyper.*` |

### Module `reasoning_engine.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/core/reasoning_engine.py` | `DEPRECATED` | 2076 | `models.schemas, typing` | Preserve as historical reference (Deprecated) |
| `archive_engines/boundary_perfect_ai/reasoning_engine.py` | `DEPRECATED` | 1538 | `archive_engines.hybrid_os_symbolic.symbolic_core, intel_core_ai.inference, logging, typing` | Preserve as historical reference (Deprecated) |
| `backend/core/reasoning_engine.py` | `ACTIVE_SOURCE` | 10446 | `logging, time, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `reasoning_loop.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/llm_os_intel/reasoning_loop.py` | `DEPRECATED` | 1895 | `archive_engines.llm_os_intel.memory, intel_core_ai.inference, logging` | Preserve as historical reference (Deprecated) |
| `execution/reasoning_loop.py` | `ACTIVE_SOURCE` | 303 | `execution.execution` | Preserve for compatibility / migrate to `hyper.*` |

### Module `reconstruction_engine.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper/reconstruction/reconstruction_engine.py` | `ACTIVE_SOURCE` | 1761 | `numpy, time, typing` | **Retain as Authoritative Source of Truth** |
| `hyper_x/reconstruction/reconstruction_engine.py` | `ACTIVE_SOURCE` | 3290 | `__future__, dataclasses, enum, numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `redundancy.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_mvc_dar/redundancy.py` | `ACTIVE_SOURCE` | 1546 | `hashlib, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/intelligence/redundancy.py` | `EXPERIMENTAL` | 1970 | `numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `refiner.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/core/refiner.py` | `ACTIVE_SOURCE` | 1094 | `logging, re` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/enhancement/refiner.py` | `ACTIVE_SOURCE` | 2289 | `logging, re, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `reflect.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/reflect/scripts/reflect.py` | `ACTIVE_SOURCE` | 5432 | `datetime, extract_signals, json, os` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/reflection/claude-reflect-system-master/reflect/scripts/reflect.py` | `ACTIVE_SOURCE` | 5432 | `datetime, extract_signals, json, os` | Preserve for compatibility / migrate to `hyper.*` |

### Module `reliability.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/fallback_modes/reliability.py` | `DEPRECATED` | 1995 | `enum, logging, psutil, typing` | Preserve as historical reference (Deprecated) |
| `backend/core/reliability.py` | `ACTIVE_SOURCE` | 3720 | `backend.observability.telemetry, time, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `report_generator.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper/reporting/report_generator.py` | `ACTIVE_SOURCE` | 1912 | `typing` | **Retain as Authoritative Source of Truth** |
| `hyper_v2/audit/report_generator.py` | `EXPERIMENTAL` | 9140 | `csv, hyper_v2.audit.benchmark_runner, hyper_v2.audit.holdout_runner, json` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/audit/report_generator.py` | `EXPERIMENTAL` | 13021 | `csv, hyper_v3.benchmark.holdout, hyper_v3.benchmark.runner, hyper_v3.learning.hardware_model` | Preserve for compatibility / migrate to `hyper.*` |

### Module `representation_search.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_v3/transforms/representation_search.py` | `EXPERIMENTAL` | 3371 | `hyper_v3.transforms.factorization, hyper_v3.transforms.representation, hyper_v3.transforms.sparse, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/representations/representation_search.py` | `ACTIVE_SOURCE` | 4544 | `__future__, dataclasses, enum, numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `residual_engine.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper/residual/residual_engine.py` | `ACTIVE_SOURCE` | 2092 | `numpy, time, typing` | **Retain as Authoritative Source of Truth** |
| `hyper_cco/residual_engine.py` | `ACTIVE_SOURCE` | 17500 | `__future__, contract, dataclasses, enum` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/residual_engine.py` | `ACTIVE_SOURCE` | 5709 | `__future__, dataclasses, hyper_x.wormhole_compiler.contract_ir, numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `resource_manager.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/os/resource_manager.py` | `ACTIVE_SOURCE` | 3036 | `logging, psutil, threading, time` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper/resource/resource_manager.py` | `ACTIVE_SOURCE` | 1793 | `numpy, typing` | **Retain as Authoritative Source of Truth** |

### Module `retriever.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/orchestration/retriever.py` | `DEPRECATED` | 1289 | `backend.intelligence.rag, logging, typing` | Preserve as historical reference (Deprecated) |
| `rag/retriever.py` | `ACTIVE_SOURCE` | 4298 | `logging, numpy, retrieval.lsh_engine, retrieval.vsa_engine` | Preserve for compatibility / migrate to `hyper.*` |

### Module `router.py` (13 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_compute_router/router.py` | `DEPRECATED` | 2019 | `logging, random, typing` | Preserve as historical reference (Deprecated) |
| `archive_engines/adaptive_self_correcting_system/core/router.py` | `DEPRECATED` | 752 | `hardness` | Preserve as historical reference (Deprecated) |
| `archive_engines/adaptive_self_correcting_system/project_hyper_perceived/core/router.py` | `DEPRECATED` | 1031 | `detector, perception.layer, schemas.contracts` | Preserve as historical reference (Deprecated) |
| `archive_engines/hybrid_ai_system/core/router.py` | `DEPRECATED` | 875 | `enum` | Preserve as historical reference (Deprecated) |
| `archive_engines/hybrid_intel_ai/router.py` | `DEPRECATED` | 7519 | `intel_core_ai.inference, json, logging, random` | Preserve as historical reference (Deprecated) |
| `archive_engines/hybrid_os_symbolic/router.py` | `DEPRECATED` | 3338 | `asyncio, intel_core_ai.inference, json, logging` | Preserve as historical reference (Deprecated) |
| `archive_engines/hyper_optimized_ai/app/core/router.py` | `DEPRECATED` | 2955 | `enum, typing` | Preserve as historical reference (Deprecated) |
| `archive_engines/steered_intel_ai/router.py` | `DEPRECATED` | 1615 | `intel_core_ai.inference, json, logging, typing` | Preserve as historical reference (Deprecated) |
| `backend/hardware/router.py` | `ACTIVE_SOURCE` | 12937 | `__future__, backend.hardware.detector, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/intelligence/router.py` | `ACTIVE_SOURCE` | 9822 | `backend.core.logging, backend.core.middleware, backend.hybrid.intent, faiss` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/micro_models/router.py` | `ACTIVE_SOURCE` | 1842 | `asyncio, backend.models.llm_loader, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `experts/router.py` | `ACTIVE_SOURCE` | 7162 | `experts.domain_experts, logging, numpy, re` | Preserve for compatibility / migrate to `hyper.*` |
| `project_hyper/router.py` | `ACTIVE_SOURCE` | 756 | `none` | Preserve for compatibility / migrate to `hyper.*` |

### Module `runtime.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper100/runtime.py` | `EXPERIMENTAL` | 11174 | `adaptive_fallback, cache_reuse_engine, contract_engine, elimination_engine` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_cel/runtime.py` | `ACTIVE_SOURCE` | 5664 | `hyper_cel.contract.contract, hyper_cel.contract.verifier, hyper_cel.execution.cpu, hyper_cel.execution.hybrid` | Preserve for compatibility / migrate to `hyper.*` |

### Module `sandbox.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/vibethinker/execution/actions/sandbox.py` | `ACTIVE_SOURCE` | 632 | `backend.vibethinker.execution.registry, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper/security/sandbox.py` | `ACTIVE_SOURCE` | 1250 | `time, typing` | **Retain as Authoritative Source of Truth** |

### Module `scheduler.py` (4 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/performance/scheduler.py` | `ACTIVE_SOURCE` | 1383 | `asyncio, backend.observability.telemetry, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_cco/scheduler.py` | `ACTIVE_SOURCE` | 8988 | `dataclasses, enum, numpy, openvino.runtime` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v2/execution/scheduler.py` | `EXPERIMENTAL` | 1232 | `hyper_v2.compiler.intermediate_representation, hyper_v2.execution.cpu_backend, hyper_v2.execution.hybrid_backend, hyper_v2.execution.igpu_backend` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/runtime/scheduler.py` | `EXPERIMENTAL` | 1071 | `hyper_v3.ir.operation, hyper_v3.runtime.cpu_backend, hyper_v3.runtime.hybrid_backend, hyper_v3.runtime.igpu_backend` | Preserve for compatibility / migrate to `hyper.*` |

### Module `schemas.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/models/schemas.py` | `DEPRECATED` | 691 | `datetime, enum, pydantic, typing` | Preserve as historical reference (Deprecated) |
| `hyper_x/wormhole_compiler/schemas.py` | `ACTIVE_SOURCE` | 11394 | `__future__, dataclasses, enum, hashlib` | Preserve for compatibility / migrate to `hyper.*` |

### Module `scientific_auditor.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_x/scientific_auditor.py` | `ACTIVE_SOURCE` | 3907 | `__future__, argparse, hyper_x.hardware.fingerprint, hyper_x.wormhole_compiler.claim_validator` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/scientific_auditor.py` | `ACTIVE_SOURCE` | 6693 | `__future__, dataclasses, re, time` | Preserve for compatibility / migrate to `hyper.*` |

### Module `scope_analyzer.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/reflect/scripts/scope_analyzer.py` | `ACTIVE_SOURCE` | 8497 | `argparse, hashlib, json, learning_ledger` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/reflection/claude-reflect-system-master/reflect/scripts/scope_analyzer.py` | `ACTIVE_SOURCE` | 8497 | `argparse, hashlib, json, learning_ledger` | Preserve for compatibility / migrate to `hyper.*` |

### Module `scorecard.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_cco/scorecard.py` | `ACTIVE_SOURCE` | 35014 | `contract, dataclasses, hashlib, json` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/strict/scorecard.py` | `ACTIVE_SOURCE` | 9376 | `__future__, dataclasses, json, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `security.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/core/security.py` | `ACTIVE_SOURCE` | 8217 | `fastapi, fastapi.middleware.cors, fastapi.security, firebase_admin` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/db/security.py` | `ACTIVE_SOURCE` | 588 | `sqlalchemy, sqlalchemy.engine, sqlalchemy.orm, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `security_audit.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `scripts/security/security_audit.py` | `ACTIVE_SOURCE` | 2232 | `json, requests` | Preserve for compatibility / migrate to `hyper.*` |
| `scripts/security_audit.py` | `ACTIVE_SOURCE` | 1842 | `json, pathlib, subprocess` | Preserve for compatibility / migrate to `hyper.*` |

### Module `security_sandbox.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/security/security_sandbox.py` | `ACTIVE_SOURCE` | 6085 | `ast, base64, hashlib, io` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/security_sandbox.py` | `ACTIVE_SOURCE` | 8346 | `__future__, ast, dataclasses, inspect` | Preserve for compatibility / migrate to `hyper.*` |

### Module `self_optimizer.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/optimization/self_optimizer.py` | `ACTIVE_SOURCE` | 6534 | `collections, json, logging, os` | Preserve for compatibility / migrate to `hyper.*` |
| `core/quantum/optimization/self_optimizer.py` | `ACTIVE_SOURCE` | 1404 | `logging, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `semantic_cache.py` (11 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/cache/semantic_cache.py` | `DEPRECATED` | 1566 | `faiss, models.schemas, numpy, sentence_transformers` | Preserve as historical reference (Deprecated) |
| `archive_engines/adaptive_self_correcting_system/project_hyper/cache/semantic_cache.py` | `DEPRECATED` | 1057 | `numpy, typing` | Preserve as historical reference (Deprecated) |
| `archive_engines/orchestration/intelligence/semantic_cache.py` | `DEPRECATED` | 2588 | `faiss, json, logging, numpy` | Preserve as historical reference (Deprecated) |
| `backend/cache/semantic_cache.py` | `ACTIVE_SOURCE` | 16977 | `backend.core.db_utils, faiss, hashlib, logging` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/caching/semantic_cache.py` | `ACTIVE_SOURCE` | 9956 | `faiss, logging, numpy, onnxruntime` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/layer1_memory/semantic_cache.py` | `ACTIVE_SOURCE` | 7107 | `backend.core.db_utils, hashlib, logging, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `core/quantum/caching/semantic_cache.py` | `ACTIVE_SOURCE` | 1802 | `faiss, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/resonance/semantic_cache.py` | `ACTIVE_SOURCE` | 2486 | `__future__, logging, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/semantic_cache.py` | `ACTIVE_SOURCE` | 9325 | `faiss, hashlib, logging, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v2/cache/semantic_cache.py` | `EXPERIMENTAL` | 1402 | `numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/pathway_search/semantic_cache.py` | `ACTIVE_SOURCE` | 2036 | `numpy, time, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `semantic_detector.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/reflect/scripts/semantic_detector.py` | `ACTIVE_SOURCE` | 8256 | `json, subprocess, sys, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/reflection/claude-reflect-system-master/reflect/scripts/semantic_detector.py` | `ACTIVE_SOURCE` | 8256 | `json, subprocess, sys, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `semantic_router.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/orchestration/semantic_router.py` | `DEPRECATED` | 3891 | `logging, typing` | Preserve as historical reference (Deprecated) |
| `hyper_runtime/adaptive_routing/semantic_router.py` | `ACTIVE_SOURCE` | 1184 | `numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `server.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/server.py` | `ACTIVE_SOURCE` | 7055 | `backend.layer4_igpu.openvino_igpu_engine, backend.layer5_local_infer.bitnet_tmac_engine, backend.layer5_local_infer.native_engine, core_ai.cache_manager` | Preserve for compatibility / migrate to `hyper.*` |
| `dashboard/server.py` | `ACTIVE_SOURCE` | 5238 | `asyncio, http.server, json, logging` | Preserve for compatibility / migrate to `hyper.*` |

### Module `setup.py` (4 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `HYPER_v6_BREAKTHROUGH/setup.py` | `ACTIVE_SOURCE` | 3500 | `argparse, cache_engine, json, os` | Preserve for compatibility / migrate to `hyper.*` |
| `leo_infinity_kernels/dfa_engine/setup.py` | `ACTIVE_SOURCE` | 1565 | `os, pybind11, setuptools, setuptools.command.build_ext` | Preserve for compatibility / migrate to `hyper.*` |
| `leo_infinity_kernels/setup.py` | `ACTIVE_SOURCE` | 1488 | `setuptools` | Preserve for compatibility / migrate to `hyper.*` |
| `setup.py` | `ACTIVE_SOURCE` | 819 | `os, setuptools, torch.utils` | Preserve for compatibility / migrate to `hyper.*` |

### Module `sparse_attention.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_runtime/sparse_attention.py` | `ACTIVE_SOURCE` | 6648 | `numpy, time, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `phoenix/sparse_attention.py` | `EXPERIMENTAL` | 2975 | `math, torch, torch.nn, torch.nn.functional` | Preserve for compatibility / migrate to `hyper.*` |

### Module `sparse_engine.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/inference/sparse_engine.py` | `ACTIVE_SOURCE` | 2936 | `__future__, asyncio, backend.layer5_local_infer.bitnet_tmac_engine, logging` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/layer9_optimization/sparse_engine.py` | `ACTIVE_SOURCE` | 1683 | `logging, time, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `sparsity.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_mvc_dar/sparsity.py` | `ACTIVE_SOURCE` | 1360 | `numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/intelligence/sparsity.py` | `EXPERIMENTAL` | 1954 | `numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `sparsity_engine.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper/sparsity/sparsity_engine.py` | `ACTIVE_SOURCE` | 1832 | `numpy, scipy.sparse, time, typing` | **Retain as Authoritative Source of Truth** |
| `hyper100/sparsity_engine.py` | `EXPERIMENTAL` | 4145 | `dataclasses, enum, numpy, time` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_cco/sparsity_engine.py` | `ACTIVE_SOURCE` | 5237 | `dataclasses, enum, numpy, scipy.sparse` | Preserve for compatibility / migrate to `hyper.*` |

### Module `speculative.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/speculative.py` | `ACTIVE_SOURCE` | 2861 | `torch` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/ai/speculative.py` | `ACTIVE_SOURCE` | 2015 | `__future__, numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `speculative_decoder.py` (6 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/inference/speculative_decoder.py` | `ACTIVE_SOURCE` | 6120 | `__future__, asyncio, core_ai.prompt_lookup_decoder, logging` | Preserve for compatibility / migrate to `hyper.*` |
| `core/quantum/speculative/speculative_decoder.py` | `ACTIVE_SOURCE` | 7034 | `core.quantum.heterogeneous.unified_scheduler, time, torch, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/resonance/speculative_decoder.py` | `ACTIVE_SOURCE` | 1269 | `__future__, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/speculative/speculative_decoder.py` | `ACTIVE_SOURCE` | 3936 | `asyncio, hashlib, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/speculative_decoder.py` | `ACTIVE_SOURCE` | 9850 | `llama_cpp, logging, numpy, os` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_runtime/speculative_decoding/speculative_decoder.py` | `ACTIVE_SOURCE` | 3885 | `draft_model, logging, replay_assisted_speculation, time` | Preserve for compatibility / migrate to `hyper.*` |

### Module `speculative_engine.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/core/speculative_engine.py` | `DEPRECATED` | 636 | `typing` | Preserve as historical reference (Deprecated) |
| `core_ai/speculative_engine.py` | `ACTIVE_SOURCE` | 4564 | `time, torch, torch.nn, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `stack.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/project_hyper_perceived/fallback/stack.py` | `DEPRECATED` | 865 | `none` | Preserve as historical reference (Deprecated) |
| `archive_engines/adaptive_self_correcting_system/verifier/stack.py` | `DEPRECATED` | 3512 | `agents.breaker, models.schemas, os, subprocess` | Preserve as historical reference (Deprecated) |

### Module `strategy_memory.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_mvc_dar/strategy_memory.py` | `ACTIVE_SOURCE` | 1303 | `json, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/search/strategy_memory.py` | `EXPERIMENTAL` | 1474 | `hashlib, json, os, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `suite_15.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_mvc_dar/suite_15.py` | `ACTIVE_SOURCE` | 10979 | `contract, math, numpy, time` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v2/workloads/suite_15.py` | `EXPERIMENTAL` | 25538 | `hyper_v2.compiler.contract_compiler, hyper_v2.reformulation.exact_reformulation, hyper_v2.reformulation.low_rank, hyper_v2.reformulation.sparse_reformulation` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v3/workloads/suite_15.py` | `EXPERIMENTAL` | 15487 | `hyper_v3.frontend.contract_parser, math, numpy, time` | Preserve for compatibility / migrate to `hyper.*` |

### Module `symbolic_core.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/hybrid_os_symbolic/symbolic_core.py` | `DEPRECATED` | 1776 | `logging, sympy, z3` | Preserve as historical reference (Deprecated) |
| `archive_engines/orchestration/symbolic_core.py` | `DEPRECATED` | 1928 | `logging, typing` | Preserve as historical reference (Deprecated) |

### Module `symbolic_engine.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/core/symbolic_engine.py` | `DEPRECATED` | 776 | `typing` | Preserve as historical reference (Deprecated) |
| `backend/reasoning/symbolic_engine.py` | `ACTIVE_SOURCE` | 7825 | `logging, typing, z3` | Preserve for compatibility / migrate to `hyper.*` |

### Module `task_graph.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_x/compute_fabric/task_graph.py` | `ACTIVE_SOURCE` | 8916 | `__future__, collections, hyper_x.compute_fabric.work_unit, numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `phoenix/task_graph.py` | `EXPERIMENTAL` | 3360 | `asyncio, logging, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `telemetry.py` (7 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/project_hyper/metrics/telemetry.py` | `DEPRECATED` | 882 | `none` | Preserve as historical reference (Deprecated) |
| `archive_engines/adaptive_self_correcting_system/project_hyper_final/metrics/telemetry.py` | `DEPRECATED` | 574 | `none` | Preserve as historical reference (Deprecated) |
| `backend/layer10_metrics/telemetry.py` | `ACTIVE_SOURCE` | 4496 | `logging, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `backend/observability/telemetry.py` | `ACTIVE_SOURCE` | 5572 | `logging, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_runtime/telemetry/telemetry.py` | `ACTIVE_SOURCE` | 886 | `json, psutil, time` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_v2/api/telemetry.py` | `EXPERIMENTAL` | 1605 | `time, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/telemetry.py` | `ACTIVE_SOURCE` | 9856 | `__future__, dataclasses, hashlib, json` | Preserve for compatibility / migrate to `hyper.*` |

### Module `temporal_cache.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_cel/reuse/temporal_cache.py` | `ACTIVE_SOURCE` | 2658 | `numpy, time, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_runtime/temporal_reuse/temporal_cache.py` | `ACTIVE_SOURCE` | 994 | `numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `temporal_engine.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adaptive_self_correcting_system/core/temporal_engine.py` | `DEPRECATED` | 576 | `time` | Preserve as historical reference (Deprecated) |
| `hyper/temporal/temporal_engine.py` | `ACTIVE_SOURCE` | 1982 | `numpy, time, typing` | **Retain as Authoritative Source of Truth** |

### Module `ternary_engine.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/inference/ternary_engine.py` | `ACTIVE_SOURCE` | 10190 | `__future__, asyncio, backend.layer5_local_infer.bitnet_tmac_engine, logging` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/ternary/ternary_engine.py` | `ACTIVE_SOURCE` | 4103 | `logging, numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `token_merging.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `core_ai/attention/token_merging.py` | `ACTIVE_SOURCE` | 7675 | `numpy, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_runtime/sparse_routing/token_merging.py` | `ACTIVE_SOURCE` | 2981 | `numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `tools.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/steered_intel_ai/tools.py` | `DEPRECATED` | 2005 | `ast, logging, operator, typing` | Preserve as historical reference (Deprecated) |
| `backend/core/tools.py` | `ACTIVE_SOURCE` | 2714 | `ast, datetime, logging, operator` | Preserve for compatibility / migrate to `hyper.*` |
| `project_hyper/tools.py` | `ACTIVE_SOURCE` | 1005 | `sympy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `update_skill.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `backend/reflect/scripts/update_skill.py` | `ACTIVE_SOURCE` | 8414 | `datetime, json, pathlib, re` | Preserve for compatibility / migrate to `hyper.*` |
| `core_ai/reflection/claude-reflect-system-master/reflect/scripts/update_skill.py` | `ACTIVE_SOURCE` | 8414 | `datetime, json, pathlib, re` | Preserve for compatibility / migrate to `hyper.*` |

### Module `validation.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/orchestration/validation.py` | `DEPRECATED` | 784 | `none` | Preserve as historical reference (Deprecated) |
| `archive_engines/verifier/validation.py` | `DEPRECATED` | 1559 | `logging, typing` | Preserve as historical reference (Deprecated) |

### Module `vector_db.py` (3 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/hybrid_ai_system/services/vector_db.py` | `DEPRECATED` | 2443 | `faiss, json, logging, os` | Preserve as historical reference (Deprecated) |
| `archive_engines/hyper_optimized_ai/app/services/vector_db.py` | `DEPRECATED` | 4284 | `archive_engines.hyper_optimized_ai.config, faiss, json, logging` | Preserve as historical reference (Deprecated) |
| `retrieval/vector_db.py` | `ACTIVE_SOURCE` | 1470 | `faiss, json, logging, numpy` | Preserve for compatibility / migrate to `hyper.*` |

### Module `verifier.py` (10 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `archive_engines/adversarial_verification_system/core/verifier.py` | `DEPRECATED` | 2589 | `os, pydantic, tempfile, typing` | Preserve as historical reference (Deprecated) |
| `archive_engines/closed_loop_synthesis/core/verifier.py` | `DEPRECATED` | 4178 | `archive_engines.closed_loop_synthesis.config, logging, os, pydantic` | Preserve as historical reference (Deprecated) |
| `archive_engines/perfect_verification_system/core/verifier.py` | `DEPRECATED` | 3404 | `archive_engines.perfect_verification_system.config, os, pydantic, re` | Preserve as historical reference (Deprecated) |
| `hyper/verification/verifier.py` | `ACTIVE_SOURCE` | 2154 | `numpy, time, typing` | **Retain as Authoritative Source of Truth** |
| `hyper_cco/verifier.py` | `ACTIVE_SOURCE` | 6794 | `contract, numpy, temporal_graphics, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_cel/contract/verifier.py` | `ACTIVE_SOURCE` | 1968 | `hyper_cel.contract.contract, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_runtime/runtime_verification/verifier.py` | `ACTIVE_SOURCE` | 1164 | `numpy` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/strict/verifier.py` | `ACTIVE_SOURCE` | 7004 | `__future__, dataclasses, enum, math` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/verification/verifier.py` | `ACTIVE_SOURCE` | 4579 | `__future__, adversarial, enum, holdout` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/verifier.py` | `ACTIVE_SOURCE` | 5335 | `__future__, dataclasses, hyper_x.wormhole_compiler.falsifier, hyper_x.wormhole_compiler.proof` | Preserve for compatibility / migrate to `hyper.*` |

### Module `work_ledger.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_mvc_dar/work_ledger.py` | `ACTIVE_SOURCE` | 2465 | `dataclasses, json, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/necessity/work_ledger.py` | `ACTIVE_SOURCE` | 4491 | `__future__, dataclasses, enum, typing` | Preserve for compatibility / migrate to `hyper.*` |

### Module `workload_registry.py` (2 occurrences)

| File Path | Category | Size (bytes) | Imports Sample | Recommended Action |
| :--- | :--- | :--- | :--- | :--- |
| `hyper_v3/workloads/workload_registry.py` | `EXPERIMENTAL` | 1190 | `hyper_v3.workloads.suite_15, typing` | Preserve for compatibility / migrate to `hyper.*` |
| `hyper_x/wormhole_compiler/workload_registry.py` | `ACTIVE_SOURCE` | 12681 | `__future__, dataclasses, enum, json` | Preserve for compatibility / migrate to `hyper.*` |
