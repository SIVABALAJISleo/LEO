"""
IRA Configuration — single source of truth for ALL tunable parameters.
Loads from environment variables, JSON config file, or defaults.
"""
import json
import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass
class QSMConfig:
    """Pillar 1: Quantum Semantic Mesh configuration."""
    num_tables: int = 12
    hash_bits: int = 16
    cache_dir: str = "cache/ira/qsm"
    persistence_file: str = "mesh_store.json"
    lookup_threshold: float = 0.85
    max_entries: int = 1_000_000
    embedding_dim: int = 768
    enable_persistence: bool = True
    auto_save_interval: int = 50  # Save every N new entries

@dataclass
class PSEConfig:
    """Pillar 2: Predictive Speculation Engine configuration."""
    draft_model_path: str = "models/ira/draft"
    main_model_path: str = "models/ira/main"
    speculation_length: int = 8
    acceptance_threshold: float = 0.3
    max_speculation_rounds: int = 100
    draft_device: str = "GPU"  # Intel iGPU
    main_device: str = "CPU"
    draft_threads: int = 1
    main_threads: int = 8  # All P-cores of i5-12450H
    temperature: float = 0.7
    top_p: float = 0.9

@dataclass
class ADRConfig:
    """Pillar 3: Adaptive Depth Router configuration."""
    total_layers: int = 36
    trivial_layer_count: int = 4
    simple_layer_count: int = 12
    moderate_layer_count: int = 24
    complex_layer_count: int = 36
    max_query_length_for_trivial: int = 3
    max_query_length_for_simple: int = 10
    max_query_length_for_moderate: int = 25
    classification_timeout_ms: float = 0.05

@dataclass
class NSFConfig:
    """Pillar 4: Neuro-Symbolic Fusion configuration."""
    knowledge_base_path: str = "data/ira/symbolic_kb"
    facts_file: str = "facts.json"
    templates_file: str = "templates.json"
    patterns_file: str = "patterns.json"
    max_fact_entries: int = 500_000
    symbolic_timeout_ms: float = 1.0
    hybrid_threshold: float = 0.8
    enable_code_execution: bool = True
    code_execution_timeout_ms: float = 500.0

@dataclass
class TCSConfig:
    """Pillar 5: Temporal Compute Shifter configuration."""
    idle_threshold_ms: float = 500.0
    max_predictions_per_idle: int = 5
    prediction_confidence_threshold: float = 0.3
    precompute_max_tokens: int = 128
    precompute_ttl_seconds: float = 300.0
    max_precompute_cache_size: int = 1000
    prediction_history_size: int = 100

@dataclass
class TCOConfig:
    """Pillar 6: Tri-Compute Orchestrator configuration."""
    enable_qsm: bool = True
    enable_nsf: bool = True
    enable_adr: bool = True
    enable_pse: bool = True
    enable_tcs: bool = True
    enable_ase: bool = True
    enable_cql: bool = True
    fallback_to_baseline: bool = True  # If all pillars fail
    max_total_latency_ms: float = 30000.0
    enable_detailed_breakdown: bool = True

@dataclass
class ASEConfig:
    """Pillar 7: Activation Sparsity Engine configuration."""
    sparsity_threshold: float = 0.1
    enable_sparse_forward: bool = True
    track_layer_sparsity: bool = True
    max_tracked_layers: int = 100
    adaptive_threshold: bool = True
    threshold_decay: float = 0.999

@dataclass
class CQLConfig:
    """Pillar 8: Cross-Query Learning configuration."""
    learning_db_path: str = "cache/ira/cql/learning.db"
    pattern_learning_rate: float = 1.0
    prepopulation_latency_threshold_ms: float = 100.0
    persist_interval: int = 10
    max_topic_history: int = 100
    max_pattern_entries: int = 100_000
    enable_auto_prepopulation: bool = True

@dataclass
class IRAConfig:
    """Master configuration for the entire IRA system."""
    qsm: QSMConfig = field(default_factory=QSMConfig)
    pse: PSEConfig = field(default_factory=PSEConfig)
    adr: ADRConfig = field(default_factory=ADRConfig)
    nsf: NSFConfig = field(default_factory=NSFConfig)
    tcs: TCSConfig = field(default_factory=TCSConfig)
    tco: TCOConfig = field(default_factory=TCOConfig)
    ase: ASEConfig = field(default_factory=ASEConfig)
    cql: CQLConfig = field(default_factory=CQLConfig)

    config_file_path: str = "core/ira/config/ira_config.json"
    enable_all_pillars: bool = True
    debug_mode: bool = False
    log_dir: str = "logs/ira"
    metrics_export_interval: float = 60.0  # seconds

    @classmethod
    def from_file(cls, path: str) -> 'IRAConfig':
        """Load configuration from JSON file."""
        if not os.path.exists(path):
            return cls()
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls._from_dict(data)

    @classmethod
    def from_env(cls) -> 'IRAConfig':
        """Load configuration from environment variables."""
        config = cls()
        # IRA_QSM_NUM_TABLES=12
        if os.environ.get("IRA_QSM_NUM_TABLES"):
            config.qsm.num_tables = int(os.environ["IRA_QSM_NUM_TABLES"])
        if os.environ.get("IRA_QSM_HASH_BITS"):
            config.qsm.hash_bits = int(os.environ["IRA_QSM_HASH_BITS"])
        if os.environ.get("IRA_PSE_SPECULATION_LENGTH"):
            config.pse.speculation_length = int(os.environ["IRA_PSE_SPECULATION_LENGTH"])
        if os.environ.get("IRA_DEBUG") and os.environ["IRA_DEBUG"].lower() == "true":
            config.debug_mode = True
        if os.environ.get("IRA_LOG_DIR"):
            config.log_dir = os.environ["IRA_LOG_DIR"]
        if os.environ.get("IRA_DRAFT_DEVICE"):
            config.pse.draft_device = os.environ["IRA_DRAFT_DEVICE"]
        if os.environ.get("IRA_MAIN_DEVICE"):
            config.pse.main_device = os.environ["IRA_MAIN_DEVICE"]
        return config

    @classmethod
    def _from_dict(cls, data: dict) -> 'IRAConfig':
        """Recursively build config from dict."""
        config = cls()
        if "qsm" in data:
            for k, v in data["qsm"].items():
                if hasattr(config.qsm, k):
                    setattr(config.qsm, k, v)
        if "pse" in data:
            for k, v in data["pse"].items():
                if hasattr(config.pse, k):
                    setattr(config.pse, k, v)
        if "adr" in data:
            for k, v in data["adr"].items():
                if hasattr(config.adr, k):
                    setattr(config.adr, k, v)
        if "nsf" in data:
            for k, v in data["nsf"].items():
                if hasattr(config.nsf, k):
                    setattr(config.nsf, k, v)
        if "tcs" in data:
            for k, v in data["tcs"].items():
                if hasattr(config.tcs, k):
                    setattr(config.tcs, k, v)
        if "tco" in data:
            for k, v in data["tco"].items():
                if hasattr(config.tco, k):
                    setattr(config.tco, k, v)
        if "ase" in data:
            for k, v in data["ase"].items():
                if hasattr(config.ase, k):
                    setattr(config.ase, k, v)
        if "cql" in data:
            for k, v in data["cql"].items():
                if hasattr(config.cql, k):
                    setattr(config.cql, k, v)
        if "enable_all_pillars" in data:
            config.enable_all_pillars = data["enable_all_pillars"]
        if "debug_mode" in data:
            config.debug_mode = data["debug_mode"]
        return config

    def to_file(self, path: str = None):
        """Save current configuration to JSON file."""
        path = path or self.config_file_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {
            "qsm": self.qsm.__dict__,
            "pse": self.pse.__dict__,
            "adr": self.adr.__dict__,
            "nsf": self.nsf.__dict__,
            "tcs": self.tcs.__dict__,
            "tco": self.tco.__dict__,
            "ase": self.ase.__dict__,
            "cql": self.cql.__dict__,
            "enable_all_pillars": self.enable_all_pillars,
            "debug_mode": self.debug_mode,
            "log_dir": self.log_dir
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
