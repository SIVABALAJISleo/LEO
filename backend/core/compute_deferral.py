"""
backend/core/compute_deferral.py

Compute Deferral System (AIS++ Module 8)
=========================================
If heavy compute is required:
  → Return partial answer INSTANTLY (< 5ms)
  → Defer full compute to background (non-blocking)
  → Push improved answer to client silently (via update store)

Architecture:
  - Instant response: skeleton + estimated confidence metadata
  - Background job: full pipeline resolution
  - Update store: maps request_id → improved answer when ready
  - Polling API: client can check /api/v1/updates/{request_id}

Rules:
  - NEVER block the client for heavy compute
  - Deferred job MUST run (no silent drops)
  - Update stored permanently (not ephemeral)
  - Background compute uses high priority
  - Skeleton answer always honest about being partial
"""
import logging
import asyncio
import time
import json
import os
from typing import Dict, Any, Optional
from collections import OrderedDict

logger = logging.getLogger(__name__)

UPDATES_PATH  = os.path.join(os.getcwd(), "data", "deferred_updates.json")
MAX_UPDATES   = 10_000    # max pending update records
HEAVY_COMPUTE_THRESHOLD_MS = 50.0  # if we predict >50ms → defer


class DeferredUpdateStore:
    """
    Stores completed deferred results keyed by request_id.
    Clients poll this store for their improved answers.
    """
    def __init__(self):
        self._store: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._load()

    def register_deferred(self, request_id: str, query: str, skeleton: str) -> None:
        self._store[request_id] = {
            "request_id":   request_id,
            "query":        query,
            "skeleton":     skeleton,
            "full_answer":  None,
            "status":       "pending",
            "created_at":   time.time(),
            "resolved_at":  None,
        }
        if len(self._store) > MAX_UPDATES:
            # Evict oldest
            self._store.popitem(last=False)

    def resolve(self, request_id: str, full_answer: str, confidence: float, mode: str) -> None:
        if request_id in self._store:
            entry = self._store[request_id]
            entry["full_answer"]  = full_answer
            entry["confidence"]   = confidence
            entry["mode"]         = mode
            entry["status"]       = "resolved"
            entry["resolved_at"]  = time.time()
            self._save()
            logger.info(f"deferred.resolved: req={request_id} conf={confidence:.3f}")

    def get(self, request_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(request_id)

    def is_pending(self, request_id: str) -> bool:
        entry = self._store.get(request_id)
        return entry is not None and entry["status"] == "pending"

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(UPDATES_PATH), exist_ok=True)
            # Only persist last 1000 for speed
            recent = dict(list(self._store.items())[-1000:])
            with open(UPDATES_PATH, "w", encoding="utf-8") as f:
                json.dump(recent, f)
        except Exception as exc:
            logger.warning(f"deferred.save_error: {exc}")

    def _load(self) -> None:
        if not os.path.exists(UPDATES_PATH):
            return
        try:
            with open(UPDATES_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._store.update(data)
            logger.info(f"deferred.loaded: {len(self._store)} records")
        except Exception:
            pass

    def stats(self) -> Dict[str, Any]:
        resolved = sum(1 for v in self._store.values() if v["status"] == "resolved")
        pending  = sum(1 for v in self._store.values() if v["status"] == "pending")
        avg_resolve_time = 0.0
        times = [
            v["resolved_at"] - v["created_at"]
            for v in self._store.values()
            if v.get("resolved_at") and v.get("created_at")
        ]
        if times:
            avg_resolve_time = sum(times) / len(times)
        return {
            "total":            len(self._store),
            "resolved":         resolved,
            "pending":          pending,
            "avg_resolve_secs": round(avg_resolve_time, 2),
        }


class ComputeDeferralSystem:
    """
    Handles heavy compute by returning instant partial answers
    and deferring full resolution to background.
    """

    def __init__(self):
        self.update_store = DeferredUpdateStore()
        self._deferrals: int = 0

    def should_defer(self, elapsed_ms: float, confidence: float) -> bool:
        """
        Returns True if the system should defer full compute and return skeleton.
        Triggers when:
          - elapsed time is already high (>50ms)
          - confidence is low (<0.85) — full compute needed but expensive
        """
        return elapsed_ms > HEAVY_COMPUTE_THRESHOLD_MS or confidence < 0.85

    def instant_skeleton(self, query: str, request_id: str, reason: str = "") -> Dict[str, Any]:
        """
        Creates and returns an instant partial response.
        Also registers the request_id in update_store for polling.
        """
        skeleton_text = (
            f"Analyzing query: '{query}'. "
            "An initial response is being prepared while the full answer is computed. "
            f"{reason + ' ' if reason else ''}"
            f"Check /api/v1/updates/{request_id} for the complete answer."
        )
        self.update_store.register_deferred(request_id, query, skeleton_text)
        self._deferrals += 1

        logger.info(f"deferral.skeleton_sent: req={request_id} reason='{reason}'")
        return {
            "result":        skeleton_text,
            "mode":          "deferred_skeleton",
            "confidence":    0.4,
            "is_partial":    True,
            "update_url":    f"/api/v1/updates/{request_id}",
            "request_id":    request_id,
        }

    async def defer_and_resolve(
        self,
        query: str,
        request_id: str,
        tenant_id: str,
        session_id: str,
        bg_compute,
    ) -> None:
        """
        Enqueues the full resolution in background.
        When done, stores result in update_store via resolve().
        """
        async def _resolve_and_update():
            try:
                from backend.background.precompute_pipeline import global_precompute_pipeline
                result = await global_precompute_pipeline.resolve_and_store(
                    query, tenant_id, "DEFERRAL", session_id
                )
                if result:
                    self.update_store.resolve(
                        request_id,
                        result.get("answer", ""),
                        float(result.get("confidence", 0.9)),
                        "deferred_full_compute",
                    )
            except Exception as exc:
                logger.error(f"deferral.resolve_error: req={request_id} {exc}")

        asyncio.create_task(_resolve_and_update())
        logger.info(f"deferral.resolution_launched: req={request_id}")

    def stats(self) -> Dict[str, Any]:
        return {
            "total_deferrals": self._deferrals,
            "update_store":    self.update_store.stats(),
        }


global_compute_deferral = ComputeDeferralSystem()
