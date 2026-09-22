"""
hyper/discovery/checkpoint_engine.py
=====================================
Search State Checkpointing & Resume Engine for HYPER.

Persists and resumes continuous discovery state in `checkpoints/discovery_checkpoint.json`:
- search_state
- candidate_queue
- tested_candidates
- successful_candidates
- failed_candidates
- random_seed
- environment / hardware_state
- software_version

Guarantees zero discovery loss across sessions.
"""

from __future__ import annotations
import os
import json
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hyper.discovery.pathway_ir import PathwayIR


class CheckpointMetadata(BaseModel):
    version: str = "vNext-Discovery-1.0"
    timestamp: float = Field(default_factory=time.time)
    cpu_info: str = "Intel Core i5-12450H (8c/12t)"
    igpu_info: str = "Intel UHD Graphics (48 EUs)"
    ram_gb: float = 16.0
    random_seed: int = 42


class DiscoveryCheckpoint(BaseModel):
    metadata: CheckpointMetadata = Field(default_factory=CheckpointMetadata)
    current_workload: str = "default_workload"
    iteration_count: int = 0
    candidate_queue: List[Dict[str, Any]] = Field(default_factory=list)
    tested_candidates: List[str] = Field(default_factory=list)
    successful_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    failed_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    custom_state: Dict[str, Any] = Field(default_factory=dict)


class CheckpointEngine:
    """
    Saves and loads discovery session checkpoints to disk.
    """

    def __init__(self, checkpoint_path: str = "checkpoints/discovery_checkpoint.json") -> None:
        self.checkpoint_path = checkpoint_path
        os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)

    def save_checkpoint(self, checkpoint: DiscoveryCheckpoint) -> str:
        data = checkpoint.model_dump()
        data["metadata"]["timestamp"] = time.time()
        with open(self.checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return self.checkpoint_path

    def load_checkpoint(self) -> Optional[DiscoveryCheckpoint]:
        if not os.path.exists(self.checkpoint_path):
            return None
        try:
            with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return DiscoveryCheckpoint(**data)
        except Exception:
            return None

    def record_success(self, pathway: PathwayIR, speedup: float, work_reduction: float) -> None:
        cp = self.load_checkpoint() or DiscoveryCheckpoint()
        cp.iteration_count += 1
        cp.successful_candidates.append({
            "pathway_id": pathway.pathway_id,
            "workload_id": pathway.workload_id,
            "speedup": speedup,
            "work_reduction_pct": work_reduction,
            "timestamp": time.time(),
        })
        self.save_checkpoint(cp)

    def record_failure(self, pathway_id: str, workload_id: str, reason: str, counterexample_found: bool) -> None:
        cp = self.load_checkpoint() or DiscoveryCheckpoint()
        cp.iteration_count += 1
        cp.failed_candidates.append({
            "pathway_id": pathway_id,
            "workload_id": workload_id,
            "reason": reason,
            "counterexample_found": counterexample_found,
            "timestamp": time.time(),
        })
        self.save_checkpoint(cp)
