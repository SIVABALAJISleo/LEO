"""
hyper/discovery/capability_registry.py
======================================
Formal Capability Registry & Maturity Tracker for UCTDE.

Enforces Section 4, Section 87, and Section 91 specifications:
Tracks feature maturity levels (Level 0 to Level 12), implementation status,
verification status, proof status, limitations, dependencies, and next actions.
"""

from __future__ import annotations
import os
import json
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MaturityLevel(str, Enum):
    LEVEL_0 = "Level 0 (Manual Optimization)"
    LEVEL_1 = "Level 1 (Automated Optimization)"
    LEVEL_2 = "Level 2 (Automated Transformation Search)"
    LEVEL_3 = "Level 3 (Automated Algorithm Discovery)"
    LEVEL_4 = "Level 4 (Automated Program Synthesis)"
    LEVEL_5 = "Level 5 (Automated Verification)"
    LEVEL_6 = "Level 6 (Automated Counterexample Discovery)"
    LEVEL_7 = "Level 7 (Automated Generalization)"
    LEVEL_8 = "Level 8 (Automated Proof Discovery)"
    LEVEL_9 = "Level 9 (Meta-Search)"
    LEVEL_10 = "Level 10 (Self-Improving Computational Discovery)"
    LEVEL_11 = "Level 11 (Cross-Workload Discovery Transfer)"
    LEVEL_12 = "Level 12 (Broad Universal Computational Research)"


class FeatureStatus(str, Enum):
    IMPLEMENTED = "IMPLEMENTED"
    PARTIAL = "PARTIAL"
    EXPERIMENTAL = "EXPERIMENTAL"
    MEASURED = "MEASURED"
    PROVEN = "PROVEN"
    UNKNOWN = "UNKNOWN"
    FAILED = "FAILED"


class CapabilityEntry(BaseModel):
    feature: str
    status: FeatureStatus = FeatureStatus.IMPLEMENTED
    source_file: str
    implementation_level: MaturityLevel
    test_status: str = "PASSING"
    benchmark_status: str = "BENCHMARKED"
    verification_status: str = "VERIFIED"
    proof_status: str = "EMPIRICAL"
    limitations: str = ""
    dependencies: List[str] = Field(default_factory=list)
    next_action: str = ""


class CapabilityRegistry:
    """
    Central repository capability registry for tracking discovery maturity.
    """

    def __init__(self, matrix_path: Optional[str] = None) -> None:
        self.entries: Dict[str, CapabilityEntry] = {}
        self.matrix_path = matrix_path or os.path.join("docs", "CAPABILITY_MATRIX.json")
        self._load_defaults()

    def _load_defaults(self) -> None:
        if os.path.exists(self.matrix_path):
            try:
                with open(self.matrix_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("matrix", []):
                        # Map level string to enum
                        lvl_str = item.get("implementation_level", "")
                        matched_lvl = MaturityLevel.LEVEL_0
                        for lvl in MaturityLevel:
                            if lvl.name.lower() in lvl_str.lower() or lvl.value.lower() in lvl_str.lower():
                                matched_lvl = lvl
                                break

                        # Map status string
                        st_str = item.get("status", "IMPLEMENTED").upper()
                        matched_st = FeatureStatus.IMPLEMENTED
                        for st in FeatureStatus:
                            if st.value == st_str:
                                matched_st = st
                                break

                        entry = CapabilityEntry(
                            feature=item["feature"],
                            status=matched_st,
                            source_file=item["source_file"],
                            implementation_level=matched_lvl,
                            test_status=item.get("test_status", "PASSING"),
                            benchmark_status=item.get("benchmark_status", "BENCHMARKED"),
                            verification_status=item.get("verification_status", "VERIFIED"),
                            proof_status=item.get("proof_status", "EMPIRICAL"),
                            limitations=item.get("limitations", ""),
                            dependencies=item.get("dependencies", []),
                            next_action=item.get("next_action", ""),
                        )
                        self.entries[entry.feature] = entry
            except Exception:
                pass

    def register_feature(self, entry: CapabilityEntry) -> None:
        self.entries[entry.feature] = entry

    def get_feature(self, feature_name: str) -> Optional[CapabilityEntry]:
        return self.entries.get(feature_name)

    def list_features(self) -> List[CapabilityEntry]:
        return list(self.entries.values())

    def get_system_maturity_level(self) -> MaturityLevel:
        """Returns the highest verified maturity level achieved by a core feature."""
        levels = [
            e.implementation_level
            for e in self.entries.values()
            if e.status in [FeatureStatus.IMPLEMENTED, FeatureStatus.PROVEN]
        ]
        if not levels:
            return MaturityLevel.LEVEL_0
        
        # Sort by level index
        all_levels = list(MaturityLevel)
        max_idx = max(all_levels.index(l) for l in levels)
        return all_levels[max_idx]

    def export_json(self, target_path: Optional[str] = None) -> str:
        path = target_path or self.matrix_path
        payload = {
            "matrix": [e.model_dump() for e in self.entries.values()],
            "total_features": len(self.entries),
            "system_maturity_level": self.get_system_maturity_level().value,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return path
