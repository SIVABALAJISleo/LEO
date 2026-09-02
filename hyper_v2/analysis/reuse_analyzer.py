"""
hyper_v2/analysis/reuse_analyzer.py
Calculates operand reuse, prefix matching, and cache residency probability.
"""

from typing import Dict, Any, List, Optional
import hashlib
import json


class ReuseAnalyzer:
    """Discovers repeated computation signatures across temporal execution traces."""

    def __init__(self):
        self._seen_signatures: Dict[str, int] = {}

    def compute_workload_fingerprint(self, op_name: str, tensor_hashes: List[str], params: Dict[str, Any]) -> str:
        payload = {
            "op": op_name,
            "inputs": tensor_hashes,
            "params": params
        }
        raw = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw.encode(), usedforsecurity=False).hexdigest()[:16]

    def record_execution(self, fingerprint: str) -> int:
        count = self._seen_signatures.get(fingerprint, 0) + 1
        self._seen_signatures[fingerprint] = count
        return count

    def check_reuse_potential(self, fingerprint: str) -> Dict[str, Any]:
        hit_count = self._seen_signatures.get(fingerprint, 0)
        return {
            "fingerprint": fingerprint,
            "previous_hits": hit_count,
            "is_frequent_pattern": hit_count >= 3,
            "estimated_reuse_benefit_ratio": 1.0 if hit_count > 0 else 0.0
        }
