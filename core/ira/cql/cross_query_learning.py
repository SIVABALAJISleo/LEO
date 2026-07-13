"""
Cross-Query Learning (CQL).
Allows the system to permanently learn from past interactions.
"""
import os
import json
import time
from collections import Counter, defaultdict, deque
from typing import List, Tuple, Dict, Any

from core.ira.shared.config import CQLConfig
from core.ira.shared.logging import IRALogger
from core.ira.shared.metrics import get_metric_collector
from core.ira.shared.text import TextNormalizer, TopicExtractor

class CrossQueryLearning:
    def __init__(self, qsm, config: CQLConfig = None):
        self.qsm = qsm
        self.config = config or CQLConfig()
        
        self.pattern_counts = Counter()
        self.topic_clusters = defaultdict(list)
        self.latency_history = deque(maxlen=10000)
        self.rephrase_history = []
        
        self.persist_counter = 0
        
        self.logger = IRALogger.get_logger("cql")
        self.metrics = get_metric_collector().system.get_or_create_pillar("cql")
        
        self._load()

    def learn_from_interaction(self, query: str, response: str,
                               latency_ms: float, was_cached: bool,
                               was_symbolic: bool, pillar_used: str) -> None:
        # 1. Extract pattern
        pattern = TextNormalizer.extract_pattern(query)
        self.pattern_counts[pattern] += 1
        
        # 2. Extract topics
        topics = TopicExtractor.extract_topics(query)
        entry = {
            "query": query,
            "response_prefix": response[:50] + "...",
            "timestamp": time.time(),
            "latency_ms": latency_ms,
            "was_cached": was_cached,
            "pillar_used": pillar_used
        }
        
        for t in topics:
            self.topic_clusters[t].append(entry)
            # Keep history bounded
            if len(self.topic_clusters[t]) > self.config.max_topic_history:
                self.topic_clusters[t] = self.topic_clusters[t][-self.config.max_topic_history:]
                
        # 3. Latency history
        self.latency_history.append(latency_ms)
        
        # 4. Auto Pre-population
        if not was_cached and not was_symbolic and latency_ms > self.config.prepopulation_latency_threshold_ms:
            if self.config.enable_auto_prepopulation:
                self._auto_prepopulate(query, response)
                
        # 5. Persist logic
        self.persist_counter += 1
        if self.persist_counter >= self.config.persist_interval:
            self._persist()
            self.persist_counter = 0
            
        self.metrics.record_call(is_hit=True, latency_ms=0.0)

    def learn_rephrase(self, original: str, rephrased: str) -> None:
        self.rephrase_history.append((original, rephrased))
        self.logger.info(f"Learned rephrase mapping: '{original}' -> '{rephrased}'")
        self.persist_counter += 1
        if self.persist_counter >= self.config.persist_interval:
            self._persist()

    def get_popular_patterns(self, top_n: int = 20) -> List[Tuple[str, int]]:
        return self.pattern_counts.most_common(top_n)

    def get_topic_suggestions(self) -> List[str]:
        # Return topics sorted by frequency
        return sorted(self.topic_clusters.keys(), key=lambda k: len(self.topic_clusters[k]), reverse=True)

    def get_learning_progress(self) -> float:
        unique_patterns = len(self.pattern_counts)
        topic_coverage = len(self.topic_clusters)
        
        # Heuristic 0.0 to 1.0 progress score
        pattern_score = min(1.0, unique_patterns / float(self.config.max_pattern_entries))
        topic_score = min(1.0, topic_coverage / 1000.0)
        
        return (pattern_score * 0.6) + (topic_score * 0.4)

    def _auto_prepopulate(self, query: str, response: str) -> None:
        variations = self._generate_query_variations(query)
        for var in variations:
            if not self.qsm.contains(var):
                self.qsm.store(var, response, {"source": "cql_auto_prepopulate", "original": query})
        self.logger.info(f"Auto-prepopulated QSM with {len(variations)} variations of query: {query[:30]}")

    def _generate_query_variations(self, query: str) -> List[str]:
        # Simple rule-based generator for semantic variations
        variations = set()
        q_lower = query.lower()
        
        if q_lower.startswith("what is "):
            base = q_lower.replace("what is ", "", 1)
            variations.update([
                f"explain {base}", f"tell me about {base}", f"describe {base}",
                f"what do you know about {base}", f"{base} explanation"
            ])
        elif q_lower.startswith("how to "):
            base = q_lower.replace("how to ", "", 1)
            variations.update([
                f"steps for {base}", f"guide for {base}", f"{base} tutorial",
                f"way to {base}", f"method for {base}"
            ])
        elif q_lower.startswith("why is "):
            base = q_lower.replace("why is ", "", 1)
            variations.update([
                f"reason for {base}", f"cause of {base}", f"what makes {base}"
            ])
            
        # Generic tweaks
        generic = [
            f"please {q_lower}",
            f"can you {q_lower}",
            f"could you {q_lower}"
        ]
        variations.update(generic)
        
        # Ensure distinct from original
        if q_lower in variations:
            variations.remove(q_lower)
            
        return list(variations)[:5]

    def _persist(self) -> None:
        os.makedirs(os.path.dirname(self.config.learning_db_path), exist_ok=True)
        try:
            data = {
                "pattern_counts": dict(self.pattern_counts),
                "topic_clusters": {k: v[-50:] for k, v in self.topic_clusters.items()},
                "rephrase_history": self.rephrase_history[-200:],
                "stats": {
                    "progress": self.get_learning_progress()
                }
            }
            with open(self.config.learning_db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            self.logger.warning(f"Failed to persist CQL DB: {e}")

    def _load(self) -> None:
        if not os.path.exists(self.config.learning_db_path):
            return
        try:
            with open(self.config.learning_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.pattern_counts = Counter(data.get("pattern_counts", {}))
                
                # Reconstruct topic clusters
                clusters = data.get("topic_clusters", {})
                for k, v in clusters.items():
                    self.topic_clusters[k] = list(v)
                    
                self.rephrase_history = data.get("rephrase_history", [])
        except Exception as e:
            self.logger.warning(f"Failed to load CQL DB: {e}")

    def get_stats(self) -> dict:
        return {
            "total_patterns": len(self.pattern_counts),
            "total_topics": len(self.topic_clusters),
            "total_rephrases_learned": len(self.rephrase_history),
            "top_patterns": self.get_popular_patterns(5),
            "top_topics": self.get_topic_suggestions()[:5],
            "learning_progress": self.get_learning_progress(),
            "cache_contribution_estimate": sum(self.pattern_counts.values())
        }

    def optimize_qsm(self) -> None:
        # 1. Topic prepopulation
        for topic, entries in self.topic_clusters.items():
            if len(entries) > 5:
                # Naive: use the most recent response
                latest = entries[-1]
                pattern = f"tell me about {topic}"
                if not self.qsm.contains(pattern):
                    # We can't safely extract the full response from history, so we skip for now
                    # (In a full implementation, we'd lookup the response from QSM or generate it)
                    pass
                    
        # 2. Rephrase pairs mapping
        for orig, rephr in self.rephrase_history:
            orig_res = self.qsm.retrieve(orig)
            rephr_res = self.qsm.retrieve(rephr)
            
            if orig_res and not rephr_res:
                self.qsm.store(rephr, orig_res[0], {"source": "cql_rephrase_sync", "mapped_from": orig})
            elif rephr_res and not orig_res:
                self.qsm.store(orig, rephr_res[0], {"source": "cql_rephrase_sync", "mapped_from": rephr})
