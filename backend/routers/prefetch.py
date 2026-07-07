"""
backend/routers/prefetch.py
Layer 3 — Skip Sequential Token Steps: Predictive Prefetch & Negative Latency Router.
"""

from __future__ import annotations

import time
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.crystallization.crystallizer import SemanticCrystallizer
from backend.inference.speculative_decoder import global_speculative_decoder

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/prefetch", tags=["Prefetch"])

# Global state for PrefetchSlots
# Session -> { "partial_query": str, "completed_query": str, "generated_response": str, "timestamp": float }
PREFETCH_SLOTS: Dict[str, Dict[str, Any]] = {}
MAX_CONCURRENT_SLOTS = 2


class PrefetchRequest(BaseModel):
    session_id: str
    partial_query: str


class PrefetchCheckRequest(BaseModel):
    session_id: str
    final_query: str


def clean_stale_slots():
    now = time.time()
    stale_keys = [k for k, v in PREFETCH_SLOTS.items() if now - v["timestamp"] > 30.0]
    for k in stale_keys:
        PREFETCH_SLOTS.pop(k, None)


@router.post("", summary="Accept keystroke partial inputs to trigger predictive pre-generation")
async def trigger_prefetch(req: PrefetchRequest):
    clean_stale_slots()
    
    partial = req.partial_query.strip()
    if len(partial) < 5:
        return {"status": "skipped", "reason": "Query too short"}

    # Limit slot allocation to protect compute budget
    if len(PREFETCH_SLOTS) >= MAX_CONCURRENT_SLOTS and req.session_id not in PREFETCH_SLOTS:
        # Prune oldest slot
        oldest_key = min(PREFETCH_SLOTS.keys(), key=lambda k: PREFETCH_SLOTS[k]["timestamp"])
        PREFETCH_SLOTS.pop(oldest_key, None)

    logger.info(f"predictive_prefetch: partial_query='{partial}' for session={req.session_id}")

    # Step 1: Complete query guess (Simulated/Draft Model completion)
    completed_guess = f"{partial} architecture"
    
    # Step 2: Try crystallizer lookup
    cryst = SemanticCrystallizer()
    cryst_match = cryst.match_shortcut(completed_guess)
    
    if cryst_match:
        response_text = cryst_match["response"]
        logger.info(f"prefetch_hit: crystallized answer found for guess '{completed_guess}'")
    else:
        # Step 3: Run speculative decoding in background to warm slot
        response_text = await global_speculative_decoder.generate(completed_guess, max_tokens=25)
        logger.info(f"prefetch_hit: generated speculative preview response of size={len(response_text)}")

    PREFETCH_SLOTS[req.session_id] = {
        "partial_query": partial,
        "completed_query": completed_guess,
        "generated_response": response_text,
        "timestamp": time.time()
    }

    return {
        "status": "success",
        "session_id": req.session_id,
        "completed_guess": completed_guess,
        "response_cached": len(response_text) > 0
    }


@router.post("/check", summary="Verify final submitted query against active prefetch slot")
async def check_prefetch(req: PrefetchCheckRequest):
    final = req.final_query.strip().lower()
    slot = PREFETCH_SLOTS.get(req.session_id)

    if not slot:
        return {"hit": False, "reason": "No active prefetch slot found for this session"}

    completed = slot["completed_query"].lower()
    
    # Jaccard index / word similarity overlap check
    final_words = set(final.split())
    completed_words = set(completed.split())
    
    intersection = final_words.intersection(completed_words)
    union = final_words.union(completed_words)
    similarity = len(intersection) / len(union) if union else 0.0

    # Clean the slot immediately upon check (single-use constraint)
    PREFETCH_SLOTS.pop(req.session_id, None)

    if similarity > 0.70:
        logger.info(f"prefetch_verified_hit: similarity={similarity:.2f}. Serving negative-latency cache.")
        return {
            "hit": True,
            "response": slot["generated_response"],
            "similarity": similarity
        }

    return {
        "hit": False,
        "reason": f"Low query match similarity ({similarity:.2f})",
        "similarity": similarity
    }
