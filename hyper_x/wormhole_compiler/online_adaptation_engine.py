"""
hyper_x/wormhole_compiler/online_adaptation_engine.py
=============================================================================
HYPER-Ω: Online Adaptation Engine (Section 38)
=============================================================================
Implements the closed-loop learning cycle:

    Live Execution -> Contract Verification -> Failure Classification
         -> Prior Update -> Route Prediction Re-weighting

The engine operates in three modes:
  1. PASSIVE   - reads failure history on each call, no persistence write-back
  2. ACTIVE    - reads + writes updated priors to a JSON sidecar
  3. STREAMING - subscribes to a live telemetry queue (future / hook-based)

Key Principles:
  - Bayesian update: posterior ∝ prior × likelihood
  - Failure penalty decays exponentially with time (recency-weighted)
  - A route can only be DEMOTED, never fully suppressed (floor prior = 0.05)
  - A route is RE-PROMOTED if the same workload class succeeds on a later attempt

Failure File Schema (failures/breakthrough_failures.json):
  [
    {
      "route": "EXACT_ROW_DELTA",
      "workload_id": "...",
      "domain": "DENSE_GEMM",
      "barrier_type": "INFORMATION_BOUND",
      "timestamp": 1700000000.0
    },
    ...
  ]
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Canonical route ordering (same as BreakthroughRouter priority list)
ALL_ROUTES = [
    "EXACT_CONTENT_REUSE",
    "EXACT_CACHE",
    "EXACT_ZERO_ROW_PRUNE",
    "EXACT_SPARSE",
    "EXACT_ROW_DELTA",
    "EXACT_RESIDUAL",
    "OUTPUT_SENSITIVE",
    "EXACT_FACTORIZATION",
    "VERIFIED_ALTERNATIVE_ALGO",
    "CPU_IGPU_HETEROGENEOUS",
    "CPU_REFERENCE_FALLBACK",
]

# Default uniform prior (route_name -> log-probability weight)
_DEFAULT_PRIOR: Dict[str, float] = {r: 1.0 for r in ALL_ROUTES}

# Penalty per failure (multiplicative factor applied to prior)
_FAILURE_PENALTY = 0.80          # 20% weight reduction per observed failure
_FLOOR_PRIOR = 0.05              # Minimum prior weight to prevent total suppression
_DECAY_HALFLIFE_SECONDS = 3600.0 # Failures older than 1h decay toward 0 penalty


@dataclass
class RoutePrior:
    """Mutable Bayesian prior for a single route."""
    route: str
    weight: float = 1.0            # Unnormalised prior weight
    success_count: int = 0
    failure_count: int = 0
    last_failure_ts: float = 0.0
    last_success_ts: float = 0.0

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / max(1, total)

    def apply_failure(self, timestamp: float = 0.0) -> None:
        """Bayesian downdate: multiply weight by penalty, clamped to floor."""
        self.failure_count += 1
        self.last_failure_ts = timestamp or time.time()
        self.weight = max(_FLOOR_PRIOR, self.weight * _FAILURE_PENALTY)

    def apply_success(self, timestamp: float = 0.0) -> None:
        """Re-promote weight by recovering 50% of lost headroom."""
        self.success_count += 1
        self.last_success_ts = timestamp or time.time()
        headroom = 1.0 - self.weight
        self.weight = min(1.0, self.weight + headroom * 0.5)

    def time_decayed_weight(self, now: Optional[float] = None) -> float:
        """
        Returns effective weight adjusted for recency:
        failures further in the past contribute less penalty.
        """
        if self.last_failure_ts == 0.0:
            return self.weight
        now = now or time.time()
        age = now - self.last_failure_ts
        # Decay factor: 0.5 at half-life, 1.0 immediately after failure
        decay = math.exp(-age * math.log(2) / _DECAY_HALFLIFE_SECONDS)
        # Recovered weight approaches 1.0 as decay -> 0
        recovered = self.weight + (1.0 - self.weight) * (1.0 - decay)
        return min(1.0, max(_FLOOR_PRIOR, recovered))


@dataclass
class AdaptationState:
    """Full set of route priors for one domain class."""
    domain: str
    priors: Dict[str, RoutePrior] = field(default_factory=dict)
    total_executions: int = 0
    last_updated_ts: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        for r in ALL_ROUTES:
            if r not in self.priors:
                self.priors[r] = RoutePrior(route=r)

    def ranked_routes(self, now: Optional[float] = None) -> List[Tuple[str, float]]:
        """
        Returns routes sorted by time-decayed weight (descending).
        This is the updated prediction order after adaptation.
        """
        now = now or time.time()
        ranked = sorted(
            self.priors.items(),
            key=lambda kv: kv[1].time_decayed_weight(now),
            reverse=True,
        )
        return [(r, prior.time_decayed_weight(now)) for r, prior in ranked]

    def top_route(self, now: Optional[float] = None) -> str:
        ranked = self.ranked_routes(now)
        return ranked[0][0] if ranked else "CPU_REFERENCE_FALLBACK"


class OnlineAdaptationEngine:
    """
    Stateful engine that maintains per-domain RoutePriors and exposes:

      - record_failure(route, domain, barrier_type): downweight a route
      - record_success(route, domain):               upweight a route
      - predict_route(domain, fingerprint_hints):    return best route
      - load_from_file(path):                        replay past failures
      - export_priors(path):                         persist priors to JSON
    """

    def __init__(
        self,
        failure_file: Optional[str] = None,
        mode: str = "ACTIVE",
    ) -> None:
        self.mode = mode  # PASSIVE | ACTIVE
        self.failure_file = Path(failure_file) if failure_file else Path("failures/breakthrough_failures.json")
        self.states: Dict[str, AdaptationState] = {}   # domain -> AdaptationState
        self._global_state = AdaptationState(domain="GLOBAL")

        # Auto-load on construction
        if self.failure_file.exists():
            self.load_from_file(self.failure_file)

    # ------------------------------------------------------------------
    # State Access
    # ------------------------------------------------------------------

    def _get_state(self, domain: str) -> AdaptationState:
        if domain not in self.states:
            self.states[domain] = AdaptationState(domain=domain)
        return self.states[domain]

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_failure(
        self,
        route: str,
        domain: str = "GLOBAL",
        barrier_type: str = "UNKNOWN",
        timestamp: Optional[float] = None,
        workload_id: str = "",
    ) -> None:
        """
        Applies a failure downdate to both domain-specific and global priors.
        If mode=ACTIVE, also appends to the failure JSON file.
        """
        ts = timestamp or time.time()
        state = self._get_state(domain)
        if route in state.priors:
            state.priors[route].apply_failure(ts)
        if route in self._global_state.priors:
            self._global_state.priors[route].apply_failure(ts)
        state.total_executions += 1
        state.last_updated_ts = ts

        if self.mode == "ACTIVE":
            self._append_failure_record({
                "route": route,
                "workload_id": workload_id,
                "domain": domain,
                "barrier_type": barrier_type,
                "timestamp": ts,
            })

    def record_success(
        self,
        route: str,
        domain: str = "GLOBAL",
        timestamp: Optional[float] = None,
    ) -> None:
        ts = timestamp or time.time()
        state = self._get_state(domain)
        if route in state.priors:
            state.priors[route].apply_success(ts)
        if route in self._global_state.priors:
            self._global_state.priors[route].apply_success(ts)
        state.total_executions += 1
        state.last_updated_ts = ts

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict_route(
        self,
        domain: str = "GLOBAL",
        hints: Optional[Dict[str, Any]] = None,
        exclude_routes: Optional[List[str]] = None,
    ) -> str:
        """
        Returns the highest-weighted viable route for the given domain,
        optionally excluding specific routes.
        """
        now = time.time()
        state = self._get_state(domain)
        ranked = state.ranked_routes(now)
        exclude = set(exclude_routes or [])

        # Mix in global priors: blended 70% domain / 30% global
        global_ranked = dict(self._global_state.ranked_routes(now))
        for i, (route, domain_w) in enumerate(ranked):
            global_w = global_ranked.get(route, domain_w)
            blended = 0.70 * domain_w + 0.30 * global_w
            ranked[i] = (route, blended)
        ranked.sort(key=lambda x: x[1], reverse=True)

        for route, _ in ranked:
            if route not in exclude:
                return route
        return "CPU_REFERENCE_FALLBACK"

    def get_route_weights(self, domain: str = "GLOBAL") -> Dict[str, float]:
        """Returns current time-decayed weights for all routes in a domain."""
        now = time.time()
        state = self._get_state(domain)
        return {r: p.time_decayed_weight(now) for r, p in state.priors.items()}

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def load_from_file(self, path: Optional[Path] = None) -> int:
        """
        Replays all failure records from the JSON file to reconstruct priors.
        Returns the number of records loaded.
        """
        fp = path or self.failure_file
        if not fp.exists():
            return 0

        try:
            records: List[Dict[str, Any]] = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            return 0

        loaded = 0
        for rec in records:
            route = rec.get("route", "") or rec.get("route_attempted", "")
            if route == "APPROXIMATE_LOW_RANK":
                route = "EXACT_FACTORIZATION"
            domain = rec.get("domain", "")
            wid = rec.get("workload_id", "")
            if not domain or domain == "GLOBAL":
                if wid and "GEMM" in wid:
                    domain = "DENSE_GEMM"
                else:
                    domain = "GLOBAL"
            barrier = rec.get("barrier_type", "") or rec.get("barrier_classification", "UNKNOWN")
            ts = float(rec.get("timestamp", time.time()))
            if route in ALL_ROUTES:
                # Do NOT re-append to file during replay (avoid duplication)
                old_mode, self.mode = self.mode, "PASSIVE"
                self.record_failure(route, domain, barrier, ts, wid)
                self.mode = old_mode
                loaded += 1
        return loaded

    def export_priors(self, path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Exports full prior state to a JSON file and returns the dict.
        """
        fp = path or Path("failures/adaptation_priors.json")
        fp.parent.mkdir(parents=True, exist_ok=True)
        now = time.time()

        export: Dict[str, Any] = {
            "timestamp": now,
            "mode": self.mode,
            "domains": {},
        }
        for domain, state in self.states.items():
            export["domains"][domain] = {
                "total_executions": state.total_executions,
                "ranked_routes": state.ranked_routes(now),
                "priors": {
                    r: {
                        "weight": round(p.weight, 4),
                        "decayed_weight": round(p.time_decayed_weight(now), 4),
                        "success_count": p.success_count,
                        "failure_count": p.failure_count,
                        "success_rate": round(p.success_rate, 4),
                    }
                    for r, p in state.priors.items()
                },
            }
        export["global"] = {
            "ranked_routes": self._global_state.ranked_routes(now),
        }

        fp.write_text(json.dumps(export, indent=2, default=str), encoding="utf-8")
        return export

    def summary(self) -> Dict[str, Any]:
        """Lightweight summary for dashboard reporting."""
        now = time.time()
        return {
            "domains_tracked": len(self.states),
            "total_failures_recorded": sum(
                sum(p.failure_count for p in s.priors.values())
                for s in self.states.values()
            ),
            "global_top_route": self._global_state.top_route(now),
            "per_domain_top_routes": {
                d: s.top_route(now) for d, s in self.states.items()
            },
        }

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _append_failure_record(self, record: Dict[str, Any]) -> None:
        """Appends a failure record to the JSON file (thread-unsafe, single-process)."""
        fp = self.failure_file
        fp.parent.mkdir(parents=True, exist_ok=True)
        records: List[Dict[str, Any]] = []
        if fp.exists():
            try:
                records = json.loads(fp.read_text(encoding="utf-8"))
            except Exception:
                records = []
        records.append(record)
        fp.write_text(json.dumps(records, indent=2, default=str), encoding="utf-8")
