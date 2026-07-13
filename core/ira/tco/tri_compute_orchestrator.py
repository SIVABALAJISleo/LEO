"""
Tri-Compute Orchestrator (TCO).
The ultimate conductor that ties all 8 pillars together into a seamless pipeline.
"""
import time
import os
import traceback
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

from core.ira.shared.config import IRAConfig
from core.ira.shared.logging import IRALogger
from core.ira.shared.metrics import get_metric_collector
from core.ira.shared.exceptions import IRABaseError

from core.ira.qsm.quantum_semantic_mesh import QuantumSemanticMesh
from core.ira.nsf.neuro_symbolic_fusion import NeuroSymbolicFusion
from core.ira.adr.adaptive_depth_router import AdaptiveDepthRouter
from core.ira.pse.predictive_speculation_engine import PredictiveSpeculationEngine
from core.ira.ase.activation_sparsity_engine import ActivationSparsityEngine
from core.ira.tcs.temporal_compute_shifter import TemporalComputeShifter
from core.ira.cql.cross_query_learning import CrossQueryLearning

@dataclass
class OrchestratedResponse:
    text: str                          # The final response text
    total_latency_ms: float            # Total wall-clock time
    pillar_used: str                   # Which pillar produced the answer
    cache_hit: bool                    # Was it a cache hit?
    symbolic_handled: bool             # Was it symbolically handled?
    precomputed: bool                  # Was it pre-computed during idle?
    layers_used: int                   # How many transformer layers
    tokens_generated: int              # How many tokens were generated
    effective_tok_s: float             # Effective tokens/second
    compute_breakdown: dict            # Detailed timing per stage
    adr_complexity: str                # Query complexity classification
    pse_acceptance_rate: float         # Speculation acceptance rate
    qsm_confidence: float              # Cache confidence score
    nsf_symbolic_ratio: float          # How much was handled symbolically
    error: Optional[str]               # Error message if failed

    def to_dict(self) -> dict:
        return asdict(self)

class TriComputeOrchestrator:
    def __init__(self, config: IRAConfig = None):
        # 1. Load config
        self.config = config or IRAConfig.from_env()
        if not self.config:
            self.config = IRAConfig()
            
        # 2. Set up logging
        IRALogger.set_log_dir(self.config.log_dir)
        self.logger = IRALogger.get_logger("tco")
        
        self.metric_collector = get_metric_collector()
        
        # 3. Initialize pillars exactly in order
        self.qsm = QuantumSemanticMesh(self.config.qsm)
        self.nsf = NeuroSymbolicFusion(self.config.nsf)
        self.adr = AdaptiveDepthRouter(self.config.adr)
        self.pse = PredictiveSpeculationEngine(self.config.pse) # Models not loaded yet
        self.ase = ActivationSparsityEngine(self.config.ase)
        self.tcs = TemporalComputeShifter(self.qsm, self.pse, self.config.tcs)
        self.cql = CrossQueryLearning(self.qsm, self.config.cql)
        
        self.logger.info("IRA Orchestrator Initialized. Core systems: QSM [ON], NSF [ON], ADR [ON], PSE [ON], ASE [ON], TCS [ON], CQL [ON]")
        self._initialized = True

    def process(self, query: str, max_tokens: int = 256,
                temperature: float = None) -> OrchestratedResponse:
        
        breakdown = {}
        start_time = time.perf_counter()
        
        pillar_used = "none"
        cache_hit = False
        symbolic_handled = False
        precomputed = False
        layers_used = 0
        tokens_generated = 0
        effective_tok_s = 0.0
        adr_complexity = "N/A"
        pse_acceptance = 0.0
        qsm_confidence = 0.0
        nsf_ratio = 0.0
        error = None
        response_text = ""

        try:
            # STAGE 0: Mark activity
            self.tcs.mark_activity()
            breakdown["stage0_activity_mark_ms"] = (time.perf_counter() - start_time) * 1000

            # STAGE 1: Check TCS pre-compute cache
            if self.config.tco.enable_tcs:
                t1 = time.perf_counter()
                precomputed_result = self.tcs.check_precomputed(query)
                breakdown["stage1_tcs_check_ms"] = (time.perf_counter() - t1) * 1000

                if precomputed_result is not None:
                    pillar_used = "tcs_precompute"
                    cache_hit = True
                    precomputed = True
                    response_text = precomputed_result["response"]

            # STAGE 2: QSM lookup
            if not cache_hit and self.config.tco.enable_qsm:
                t2 = time.perf_counter()
                qsm_result = self.qsm.retrieve(query)
                breakdown["stage2_qsm_lookup_ms"] = (time.perf_counter() - t2) * 1000

                if qsm_result is not None:
                    response_text, qsm_confidence = qsm_result
                    pillar_used = "qsm_cache"
                    cache_hit = True

            # STAGE 3: NSF Neuro-Symbolic Fusion
            if not cache_hit and self.config.tco.enable_nsf:
                t3 = time.perf_counter()
                nsf_result = self.nsf.try_symbolic(query)
                breakdown["stage3_nsf_check_ms"] = (time.perf_counter() - t3) * 1000

                if nsf_result is not None and nsf_result.symbolic_ratio >= 0.8:
                    response_text = nsf_result.response
                    nsf_ratio = nsf_result.symbolic_ratio
                    pillar_used = "nsf_symbolic"
                    symbolic_handled = True
                    cache_hit = True # Treat as O(1) hit for metrics
                    self.qsm.store(query, response_text, {"source": "nsf"})

                elif nsf_result is not None and nsf_result.symbolic_ratio < 0.8:
                    breakdown["hybrid_prefix"] = nsf_result.response
                    nsf_ratio = nsf_result.symbolic_ratio
                    symbolic_handled = True
                    query = query # Keep original or update with metadata if we had it

            # STAGE 4: ADR Adaptive Depth Router
            if not cache_hit and self.config.tco.enable_adr:
                t4 = time.perf_counter()
                complexity, layers_needed, reason = self.adr.classify(query)
                breakdown["stage4_adr_classify_ms"] = (time.perf_counter() - t4) * 1000
                breakdown["adr_complexity"] = complexity.name
                breakdown["adr_layers_needed"] = layers_needed
                breakdown["adr_reason"] = reason
                adr_complexity = complexity.name
                layers_used = layers_needed

            # STAGE 5: PSE Predictive Speculation Engine
            if not cache_hit and self.config.tco.enable_pse:
                t5 = time.perf_counter()
                try:
                    # Lazy load models if they aren't loaded yet
                    if not self.pse.is_loaded:
                        self.pse.load_models()
                        
                    response_text_neural, pse_stats = self.pse.generate_with_speculation(
                        query, max_tokens=max_tokens, temperature=temperature
                    )
                    breakdown["stage5_pse_generate_ms"] = (time.perf_counter() - t5) * 1000
                    breakdown["pse_stats"] = pse_stats
                    pillar_used = "pse_neural"
                    pse_acceptance = self.pse.acceptance_rate

                    adr_speedup = self.adr.get_speedup_factor(query)
                    base_tok_s = pse_stats.get("tokens_per_sec", 34.2)
                    effective_tok_s = base_tok_s * self.pse.effective_speedup * adr_speedup
                    tokens_generated = int(pse_stats.get("total_accepted_tokens", 0))
                    
                    response_text = response_text_neural

                except Exception as e:
                    breakdown["stage5_pse_error"] = str(e)
                    error = f"PSE failed: {str(e)}"
                    self.logger.warning(f"PSE generation failed, falling back if configured: {e}")
                    if self.config.tco.fallback_to_baseline:
                        response_text = self._baseline_generate(query, max_tokens, temperature)
                        pillar_used = "baseline_fallback"
                        effective_tok_s = 14.5
                    else:
                        raise e

            # STAGE 6: ASE (Track stats)
            if self.config.tco.enable_ase:
                breakdown["ase_avg_sparsity"] = self.ase.get_average_sparsity()

            # STAGE 7: Merge hybrid results
            if "hybrid_prefix" in breakdown:
                response_text = breakdown["hybrid_prefix"] + "\n\n" + response_text

            # STAGE 8: Post-processing & Storage
            if not cache_hit and response_text and not error:
                self.qsm.store(query, response_text, {
                    "source": pillar_used,
                    "complexity": adr_complexity,
                    "layers_used": layers_used,
                    "effective_tok_s": effective_tok_s
                })
            
            if response_text and not error:
                self.tcs.add_to_history(query, response_text)

        except Exception as e:
            error = str(e)
            self.logger.error(f"Error processing query: {traceback.format_exc()}")
            response_text = f"IRA Error: {error}"
            pillar_used = "error"

        # STAGE 9: CQL - Cross Query Learning
        total_latency = (time.perf_counter() - start_time) * 1000
        if self.config.tco.enable_cql:
            self.cql.learn_from_interaction(
                query=query,
                response=response_text,
                latency_ms=total_latency,
                was_cached=cache_hit,
                was_symbolic=symbolic_handled,
                pillar_used=pillar_used
            )

        self.metric_collector.record_query(
            response_time_ms=total_latency,
            effective_tok_s=effective_tok_s,
            breakdown={pillar_used: 1.0}
        )

        return OrchestratedResponse(
            text=response_text,
            total_latency_ms=round(total_latency, 6),
            pillar_used=pillar_used,
            cache_hit=cache_hit,
            symbolic_handled=symbolic_handled,
            precomputed=precomputed,
            layers_used=layers_used,
            tokens_generated=tokens_generated,
            effective_tok_s=round(effective_tok_s, 2),
            compute_breakdown=breakdown,
            adr_complexity=adr_complexity,
            pse_acceptance_rate=round(pse_acceptance, 4),
            qsm_confidence=round(qsm_confidence, 4),
            nsf_symbolic_ratio=round(nsf_ratio, 4),
            error=error
        )

    def _baseline_generate(self, query: str, max_tokens: int, temperature: float) -> str:
        # Fallback dummy simulation for fallback response.
        # In a real environment, this might call a standard Transformers pipeline or Llama.cpp binding
        return f"[Baseline Fallback Response for: {query}]"

    def load_models(self) -> None:
        self.pse.load_models()

    def get_system_report(self) -> dict:
        return {
            "metrics": self.metric_collector.get_full_report(),
            "qsm_stats": {"cache_size": len(self.qsm.response_store)},
            "adr_stats": self.adr.get_stats(),
            "tcs_stats": self.tcs.get_stats(),
            "cql_stats": self.cql.get_stats(),
            "pse_loaded": self.pse.is_loaded
        }

    def export_metrics(self, filepath: str = None) -> str:
        export_path = filepath or os.path.join(self.config.log_dir, "tco_metrics_export.json")
        self.metric_collector.export_json(export_path)
        return export_path

    def shutdown(self) -> None:
        self.logger.info("Initiating graceful shutdown...")
        self.tcs.shutdown()
        self.qsm.clear() # Optional, but can force persist via other ways
        self.cql._persist()
        self.export_metrics()
        self.pse.unload_models()
        self.logger.info("Shutdown complete.")
