"""
core_ai/reflection_bridge.py
=============================================================================
LEO / HYPER v6.0: Reflection & Meta-Learning Engine Bridge
=============================================================================
Connects the Claude Reflection Learning Ledger to HyperV6Engine to enable:
  1. Real-time query trace recording and signal extraction.
  2. Automatic promotion of novel, verified reasoning answers to Tier 0/1 caches.
  3. Continuous self-improvement and productivity analytics tracking.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Workspace root
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from backend.reflect.leo_reflect_service import LeoReflectService, get_reflect_service

logger = logging.getLogger("ReflectionBridge")

class HyperReflectionBridge:
    """
    Bridge connecting HYPER v6 Cognitive Router with the Reflection Learning Ledger.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.service = get_reflect_service()
        logger.info("Hyper Reflection Bridge initialized with active Learning Ledger.")

    def log_execution_trace(self, query: str, response: str, latency_ms: float, source: str, tier: int) -> Dict[str, Any]:
        """Records an execution trace into the reflection database."""
        result_payload = {
            "source": source,
            "latency_ms": latency_ms,
            "similarity": 1.0 if source == "CACHE" else 0.0,
            "response": response,
            "tier": tier
        }
        return self.service.record_query_trace(query, result_payload)

    def promote_to_cache(self, query: str, response: str, db_path: str = "hyper_v6_cache.db") -> bool:
        """Promotes a generated answer to permanent cache storage."""
        return self.service.promote_to_cache(query, response)

    def get_stats(self) -> Dict[str, Any]:
        """Returns reflection ledger telemetry and compute time saved."""
        return self.service.get_productivity_stats()
