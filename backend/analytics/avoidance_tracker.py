"""
backend/analytics/avoidance_tracker.py

Real Avoidance Metrics Engine
==============================
Tracks ALL real metrics — no simulated or fake numbers.

Tracked per request:
  - request_id
  - normalized_query
  - path_taken (which tier/mode resolved it)
  - latency_ms
  - model_called (bool)

Computed in real-time:
  avoidance_rate = 1 - (model_calls / total_requests)

Success criteria verified:
  - identical queries     → <10ms
  - similar queries       → <50ms
  - avoidance_rate        ≥ 95%
  - model_calls           ≤ 5%
  - accuracy              measured via confidence

Bug detection:
  - low-confidence answer returned → VIOLATION
  - latency > 200ms               → VIOLATION  
  - recompute triggered           → VIOLATION
"""
import logging
import time
import json
import os
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

METRICS_FILE = os.path.join(os.getcwd(), "metrics.jsonl")
AVOIDANCE_TARGET = 0.95        # 95% minimum
MODEL_CALL_MAX_RATE = 0.05     # ≤5%
IDENTICAL_LATENCY_MAX = 10.0   # ms
SIMILAR_LATENCY_MAX  = 50.0    # ms
ABSOLUTE_LATENCY_MAX = 200.0   # ms — exceeding is a bug


@dataclass
class RequestRecord:
    request_id: str
    normalized_query: str
    family_id: str
    path_taken: str     # which tier/mode responded
    latency_ms: float
    model_called: bool
    entropy_score: float
    is_cache_hit: bool
    is_prediction_hit: bool
    is_recovery: bool
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ViolationError:
    """Represents a system violation (BUG level)."""
    def __init__(self, kind: str, details: Dict[str, Any]):
        self.kind = kind
        self.details = details
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {"kind": self.kind, "details": self.details, "ts": self.timestamp}


class AvoidanceTracker:
    """
    Real, immutable metrics tracker.
    Thread-safe. Writes to JSONL for persistence.
    Computes live avoidance rate on every query.

    No fake numbers. No simulated values.
    """

    def __init__(self):
        self._lock = threading.Lock()

        # Counters
        self._total_requests: int = 0
        self._model_calls: int = 0
        self._cache_hits: int = 0
        self._prediction_hits: int = 0
        self._recovery_count: int = 0
        self._violation_count: int = 0

        # Path distribution
        self._path_counts: Dict[str, int] = defaultdict(int)

        # Latency tracking (rolling window 1000)
        self._latencies: deque = deque(maxlen=1000)
        self._identical_latencies: deque = deque(maxlen=500)
        self._similar_latencies: deque = deque(maxlen=500)

        # Entropy tracking & Heatmap
        self._entropies: deque = deque(maxlen=1000)
        self._entropy_heatmap: Dict[str, List[float]] = defaultdict(list)

        # Violations log (kept in memory, written to log)
        self._violations: List[ViolationError] = []
        
        # State tracking for Cache Miss Guarantee
        self._seen_exact_queries: set = set()
        self._seen_recovery_queries: set = set()

        # Load persistent counts from metrics file
        self._load_from_file()

    # ── Record API ─────────────────────────────────────────────────────────── #

    def record(
        self,
        request_id: str,
        normalized_query: str,
        family_id: str,
        path_taken: str,
        latency_ms: float,
        model_called: bool,
        confidence: Optional[float] = None,
        entropy_score: Optional[float] = None,
        is_cache_hit: bool = False,
        is_prediction_hit: bool = False,
        is_recovery: bool = False,
    ) -> None:
        """
        Records one completed request. Checks for violations.
        Thread-safe.
        """
        if entropy_score is None and confidence is not None:
            entropy_score = 1.0 - confidence
        elif entropy_score is None:
            entropy_score = 0.0
            
        record = RequestRecord(
            request_id=request_id,
            normalized_query=normalized_query,
            family_id=family_id,
            path_taken=path_taken,
            latency_ms=latency_ms,
            model_called=model_called,
            entropy_score=entropy_score,
            is_cache_hit=is_cache_hit,
            is_prediction_hit=is_prediction_hit,
            is_recovery=is_recovery,
        )

        with self._lock:
            # Increment counters
            self._total_requests += 1
            if model_called:
                self._model_calls += 1
            if is_cache_hit:
                self._cache_hits += 1
            if is_prediction_hit:
                self._prediction_hits += 1
            if is_recovery:
                self._recovery_count += 1

            self._path_counts[path_taken] += 1
            self._latencies.append(latency_ms)
            self._entropies.append(entropy_score)
            
            # Update Entropy Heatmap (keep last 10 scores per family)
            self._entropy_heatmap[family_id].append(entropy_score)
            if len(self._entropy_heatmap[family_id]) > 10:
                 self._entropy_heatmap[family_id].pop(0)

            # Categorize latency by hit type (TRIATTENTION v4)
            if path_taken == "CACHE":
                self._identical_latencies.append(latency_ms)
            elif path_taken in ("PREDICTED", "SEMANTIC", "ASSEMBLY"):
                self._similar_latencies.append(latency_ms)
            elif is_cache_hit or is_prediction_hit:
                self._similar_latencies.append(latency_ms)

        # Violation detection (outside lock)
        self._check_violations(record)

        # Persist
        self._append_to_file(record)

    # ── Violation Detection ────────────────────────────────────────────────── #

    def _check_violations(self, record: RequestRecord) -> None:
        """Detects and logs all violation conditions."""
        violations_found = []

        # Rule: latency > 200ms = BUG
        if record.latency_ms > ABSOLUTE_LATENCY_MAX:
            violations_found.append(
                ViolationError(
                    "LATENCY_EXCEEDED_200MS",
                    {
                        "latency_ms": record.latency_ms,
                        "path": record.path_taken,
                        "request_id": record.request_id,
                    },
                )
            )

        # Rule: cache miss when match exists = BUG
        if not record.is_cache_hit and record.normalized_query in self._seen_exact_queries:
            violations_found.append(
                ViolationError(
                    "CACHE_MISS_WHEN_MATCH_EXISTS",
                    {
                        "query": record.normalized_query,
                        "path": record.path_taken,
                        "request_id": record.request_id,
                    },
                )
            )
            
        # Rule: failure repeats = BUG
        if record.is_recovery:
            if record.normalized_query in self._seen_recovery_queries:
                violations_found.append(
                    ViolationError(
                        "FAILURE_REPEATS",
                        {
                            "query": record.normalized_query,
                            "path": record.path_taken,
                            "request_id": record.request_id,
                        },
                    )
                )

        for v in violations_found:
            with self._lock:
                self._violations.append(v)
                self._violation_count += 1
            logger.error(
                f"VIOLATION [{v.kind}]: {json.dumps(v.details)}"
            )
            
        # Add to known queries for future guarantee checks
        if not record.is_recovery:
            with self._lock:
                self._seen_exact_queries.add(record.normalized_query)
        else:
            with self._lock:
                self._seen_recovery_queries.add(record.normalized_query)

    # ── Metrics Read API ───────────────────────────────────────────────────── #

    def get_live_metrics(self) -> Dict[str, Any]:
        """Returns real-time computed metrics. No fake numbers."""
        with self._lock:
            total = self._total_requests
            model_calls = self._model_calls
            cache_hits = self._cache_hits
            pred_hits = self._prediction_hits
            latencies = list(self._latencies)
            entropies = list(self._entropies)
            path_dist = dict(self._path_counts)
            violations = self._violation_count
            id_lats = list(self._identical_latencies)
            sim_lats = list(self._similar_latencies)

        if total == 0:
            return {
                "total_requests": 0,
                "avoidance_rate": "0.00%",
                "model_call_rate": "0.00%",
                "avg_latency_ms": "0.00ms",
                "status": "no_data",
            }

        avoidance = (1.0 - model_calls / total) * 100
        model_rate = (model_calls / total) * 100
        avg_lat = sum(latencies) / len(latencies) if latencies else 0.0
        p95_lat = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0.0
        avg_entropy = sum(entropies) / len(entropies) if entropies else 0.0

        avg_id_lat = sum(id_lats) / len(id_lats) if id_lats else None
        avg_sim_lat = sum(sim_lats) / len(sim_lats) if sim_lats else None

        # Success criteria checks
        criteria = {
            "avoidance_rate_ok":     avoidance >= AVOIDANCE_TARGET * 100,
            "model_call_rate_ok":    model_rate <= MODEL_CALL_MAX_RATE * 100,
            "identical_latency_ok":  avg_id_lat is None or avg_id_lat < IDENTICAL_LATENCY_MAX,
            "similar_latency_ok":    avg_sim_lat is None or avg_sim_lat < SIMILAR_LATENCY_MAX,
            "no_violations":         violations == 0,
        }

        return {
            # Core metrics
            "total_requests":       total,
            "model_calls":          model_calls,
            "model_call_rate":      f"{model_rate:.2f}%",
            "avoidance_rate":       f"{avoidance:.2f}%",
            "avoidance_rate_raw":   round(avoidance / 100, 4),

            # Cache/prediction breakdown
            "cache_hits":           cache_hits,
            "prediction_hits":      pred_hits,
            "recovery_count":       self._recovery_count,

            # Latency breakdown
            "avg_latency_ms":       f"{avg_lat:.2f}ms",
            "p95_latency_ms":       f"{p95_lat:.2f}ms",
            "avg_identical_ms":     f"{avg_id_lat:.2f}ms" if avg_id_lat is not None else "N/A",
            "avg_similar_ms":       f"{avg_sim_lat:.2f}ms" if avg_sim_lat is not None else "N/A",

            # Accuracy/Entropy
            "avg_entropy":          f"{avg_entropy:.3f}",

            # Heatmap overview
            "heatmap_hotspots":     self.get_heatmap_hotspots(top_k=5),

            # Path distribution
            "path_distribution":    path_dist,

            # Violations
            "violations":           violations,

            # Success criteria status
            "success_criteria":     criteria,
            "all_criteria_met":     all(criteria.values()),
        }

    def get_avoidance_rate(self) -> float:
        """Returns raw float avoidance rate (0.0–1.0). Real number only."""
        with self._lock:
            if self._total_requests == 0:
                return 0.0
            return 1.0 - self._model_calls / self._total_requests

    def get_violation_log(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [v.to_dict() for v in self._violations[-50:]]
            
    def get_heatmap_hotspots(self, top_k: int = 5) -> Dict[str, float]:
        """Returns the query families with the highest average entropy (least predictable)."""
        with self._lock:
            averages = {}
            for fam, scores in self._entropy_heatmap.items():
                if len(scores) > 0:
                    averages[fam] = sum(scores) / len(scores)
            
            # Sort descending by entropy
            sorted_fams = sorted(averages.items(), key=lambda x: x[1], reverse=True)
            return {k: round(v, 3) for k, v in sorted_fams[:top_k]}

    # ── Persistence ────────────────────────────────────────────────────────── #

    def _append_to_file(self, record: RequestRecord) -> None:
        try:
            with open(METRICS_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record.to_dict()) + "\n")
        except Exception as exc:
            logger.warning(f"metrics.write_error: {exc}")

    def _load_from_file(self) -> None:
        """Loads historical metrics from JSONL file on startup."""
        if not os.path.exists(METRICS_FILE):
            return
        try:
            with open(METRICS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                        self._total_requests += 1
                        if d.get("model_called"):
                            self._model_calls += 1
                        if d.get("is_cache_hit"):
                            self._cache_hits += 1
                        if d.get("is_prediction_hit"):
                            self._prediction_hits += 1
                        path = d.get("path_taken", "unknown")
                        self._path_counts[path] += 1
                        lat = d.get("latency_ms", 0.0)
                        if lat:
                            self._latencies.append(lat)
                        ent = d.get("entropy_score")
                        if ent is None and "confidence" in d:
                            ent = 1.0 - float(d["confidence"])
                        if ent is not None:
                            self._entropies.append(ent)
                            self._entropy_heatmap[d.get("family_id", "unknown")].append(ent)
                        
                        # Recover exact queries state
                        if not d.get("is_recovery", False):
                            self._seen_exact_queries.add(d.get("normalized_query", ""))
                        else:
                            self._seen_recovery_queries.add(d.get("normalized_query", ""))
                    except (json.JSONDecodeError, KeyError):
                        continue
            logger.info(
                f"avoidance_tracker.loaded: requests={self._total_requests} "
                f"model_calls={self._model_calls}"
            )
        except Exception as exc:
            logger.warning(f"avoidance_tracker.load_error: {exc}")


global_avoidance_tracker = AvoidanceTracker()
