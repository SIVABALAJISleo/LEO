# LEO / HYPER: Integration Map & Capabilities Registry

**Document Version**: 1.0.0 (Forensic Audit & Capabilities Registry)  
**Date**: September 2026  
**Platform**: Intel Core i5-12450H + Intel UHD Graphics, 16 GB RAM, Windows 11.

---

## 1. Primary Capabilities Matrix

This registry defines the single authoritative implementation for every capability required by the LEO/HYPER mission. Conflicting or duplicate historical implementations are redirected to these canonical paths.

| Phase / Capability | Canonical Module | Key Classes / Functions | Test File |
| :--- | :--- | :--- | :--- |
| **Phase 1: Contract IR** | `hyper_cco.contract` | `WorkloadContract`, `CorrectnessClass`, `ObservableSpec` | `tests/test_cco_contracts.py` |
| **Phase 2: Observable Compiler** | `hyper_cco.observable_compiler` & `hyper_x.wormhole_compiler.observable_compiler` | `ObservableCompiler`, `ObservableIR`, `compile_observable()` | `tests/test_cbe_phase2.py` |
| **Phase 3: Information Boundary** | `hyper_cco.information_boundary` & `hyper_x.info_boundary.compiler` | `InformationBoundaryAnalyzer`, `CausalBoundaryNode` | `tests/test_cbe_phase3.py` |
| **Phase 4: Necessary-Work Compiler**| `hyper_cco.proof_elimination` | `ProofCarryingEliminationEngine`, `RegionEliminationCertificate` | `tests/test_proof_carrying_elimination.py` |
| **Phase 5: Counterfactual Elimination** | `hyper_cco.counterfactual` | `CounterfactualExecutionEngine`, `LipschitzSensitivityBound` | `tests/test_counterfactual_execution.py` |
| **Phase 6: Necessity Certificate** | `hyper_cco.proof_elimination` & `hyper_x.wormhole_compiler.necessity_certificate` | `CausalNecessityCertificate`, `RegionEliminationCertificate` | `tests/test_proof_carrying_elimination.py` |
| **Phase 7: Sufficient Representation** | `hyper_cco.semantic_compression` & `hyper_x.representations.synthesizer` | `SemanticCompressionEngine`, `RepresentationInventor` | `tests/test_semantic_compression.py` |
| **Phase 8: Algebraic Reformulation** | `hyper_x.rewrite.egraph` & `hyper_cco.contract_compiler` | `EGraph`, `EqualitySaturation`, `ContractCompiler` | `tests/test_contract_compiler.py` |
| **Phase 9: Algorithm Discovery** | `hyper_cco.algorithm_genome` & `hyper_x.discovery.algorithmic_escape_search` | `AlgorithmGenome`, `EvolveAlgorithm`, `MutateGenome` | `tests/test_algorithm_discovery.py` |
| **Phase 10: LLM Research Hypothesis**| `hyper_x.wormhole_compiler.llm_hypothesis_engine` | `HypothesisEngine`, `HypothesisRecord` | `tests/test_hyper100_falsification.py` |
| **Phase 11: 7-Mode Residuals** | `hyper_cco.residual_engine` | `ResidualEngine7Mode`, `ResidualMode` | `tests/test_residual_7modes.py` |
| **Phase 12: Computational Reuse** | `hyper_cco.exact_cache` & `hyper_cco.incremental_engine` | `ExactCache`, `IncrementalEngine` | `tests/test_cco_exact_cache.py` |
| **Phase 13: Semantic Cache Red Team**| `hyper_cco.adversarial_fuzzer` | `AdversarialContractFuzzer`, `CachePoisoningTest` | `tests/test_adversarial_contract_fuzzing.py` |
| **Phase 14 & 15: Hardware Fabric** | `hyper_cco.thermal_scheduler` & `hyper_x.hardware.fingerprint` | `ThermalAwareDeadlineScheduler`, `ExecutionTarget` | `tests/test_thermal_deadline_scheduler.py` |
| **Phase 16: Memory Optimization** | `hyper_x.wormhole_compiler.memory_movement_optimizer` | `MemoryTrafficOptimizer`, `BufferReusePlanner` | `tests/test_cbe_phase4.py` |
| **Phase 17: Canonical Hyper IR** | `hyper_x.wormhole_compiler.ir` & `hyper_cco.contract` | `HyperIR`, `NodeKind`, `TensorDescriptor` | `tests/test_cbe_phase1.py` |
| **Phase 18: Exactness Firewall** | `hyper_cco.contract` | `StrictFirewallValidator`, `CorrectnessClass` | `tests/test_cco_contracts.py` |
| **Phase 19 & 20: Independent Verifier**| `hyper_x.wormhole_compiler.functional_verifier` & `hyper_cco.contract` | `FunctionalVerifier`, `IndependentVerificationResult` | `tests/test_cco_verification.py` |
| **Phase 21: Adversarial Fuzzing** | `hyper_cco.adversarial_fuzzer` | `AdversarialContractFuzzer`, `HostilePayloadGenerator` | `tests/test_adversarial_contract_fuzzing.py` |
| **Phase 22: Blind Holdout Engine** | `hyper_x.wormhole_compiler.holdout` | `BlindHoldoutHarness`, `HoldoutVerificationSuite` | `tests/test_cbe_phase7.py` |
| **Phase 23 & 24: Benchmark Suite** | `benchmarks.run_contract_parity_benchmark` | `ContractParityBenchmarkHarness` | `benchmarks/run_contract_parity_benchmark.py` |
| **Phase 25: Metric Engine (HAE/GADR)**| `hyper_cco.cheapest_valid_path` & `hyper_x.wormhole_compiler.hardware_advantage_map` | `HardwareAdvantageMap`, `calculate_hae_gadr()` | `tests/test_cheapest_valid_path.py` |
| **Phase 26 & 27: Necessity Map** | `hyper_x.necessity_map` & `hyper_x.wormhole_compiler.schemas` | `NecessityMap`, `BarrierClassification` | `tests/test_cbe_phase5.py` |
| **Phase 32: Execution Certificate** | `hyper_cco.provenance_ledger` | `AntiCheatProvenanceLedger`, `ExecutionCertificate` | `tests/test_anti_cheat_provenance.py` |
| **Phase 39: Unified CLI** | `hyper_x.cli` | `hyper inspect`, `hyper wormhole`, `hyper verify`, etc. | `tests/test_api_suite.py` |
| **Phase 48: Claim Validator** | `hyper_x.wormhole_compiler.scientific_auditor` | `ScientificAuditor`, `validate_claim_string()` | `tests/test_scientific_auditor.py` |

---

## 2. Legacy Deprecation & Re-Routing Policy

1. **`hyper_ares/` & `hyper_cel/`**: Historical prototypes for evolutionary search and cellular automata. Forwarded to `hyper_cco.algorithm_genome` and `hyper_cco.cheapest_valid_path`.
2. **`universal_compute_router/`**: Rule-based dispatch. Forwarded to `hyper_cco.thermal_scheduler`.
3. **`hyper_v2/` & `hyper_v3/`**: Deprecated in favor of `hyper_cco.contract_compiler` and `hyper_x.rewrite`.
4. **`phoenix/` & `cosmic_singularity/`**: Retained in repository as read-only historical archives; active imports point to `hyper_cco` and `hyper_x`.
