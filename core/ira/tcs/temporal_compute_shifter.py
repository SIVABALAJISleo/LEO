"""
Temporal Compute Shifter (TCS).
Uses idle time to predict and pre-compute responses to likely follow-up queries.
"""
import time
import queue
import threading
from collections import OrderedDict, deque
from typing import List, Tuple, Optional

from core.ira.shared.config import TCSConfig
from core.ira.shared.logging import IRALogger
from core.ira.shared.metrics import get_metric_collector
from core.ira.shared.timing import PrecisionTimer
from core.ira.shared.hashing import FastHashEngine
from core.ira.shared.text import TopicExtractor

class TemporalComputeShifter:
    def __init__(self, qsm, pse, config: TCSConfig = None):
        self.qsm = qsm
        self.pse = pse
        self.config = config or TCSConfig()
        
        self.precompute_cache = OrderedDict()
        self.precompute_queue = queue.Queue()
        self.conversation_history = deque(maxlen=100)
        
        self.is_idle = False
        self.last_activity_time = time.time()
        
        self.logger = IRALogger.get_logger("tcs")
        self.metrics = get_metric_collector().system.get_or_create_pillar("tcs")
        
        self._shutdown_flag = False
        self._cache_lock = threading.Lock()
        
        # Start background threads
        self.idle_thread = threading.Thread(target=self._start_idle_detector, daemon=True)
        self.worker_thread = threading.Thread(target=self._start_precompute_worker, daemon=True)
        self.cleaner_thread = threading.Thread(target=self._start_cache_cleaner, daemon=True)
        
        self.idle_thread.start()
        self.worker_thread.start()
        self.cleaner_thread.start()

    def mark_activity(self) -> None:
        self.last_activity_time = time.time()
        self.is_idle = False

    def add_to_history(self, query: str, response: str) -> None:
        self.conversation_history.append((query, response, time.time()))

    def check_precomputed(self, query: str) -> Optional[dict]:
        timer = PrecisionTimer("check_precomputed").start()
        cache_key = FastHashEngine.sha256_short(query)
        
        with self._cache_lock:
            if cache_key in self.precompute_cache:
                entry = self.precompute_cache[cache_key]
                # Check TTL
                if (time.time() - entry["created_at"]) <= self.config.precompute_ttl_seconds:
                    # Move to end (LRU)
                    self.precompute_cache.move_to_end(cache_key)
                    elapsed = timer.stop()
                    self.metrics.record_call(is_hit=True, latency_ms=elapsed)
                    return entry
                else:
                    # Expired
                    del self.precompute_cache[cache_key]
                    
        elapsed = timer.stop()
        self.metrics.record_call(is_hit=False, latency_ms=elapsed)
        return None

    def _start_idle_detector(self) -> None:
        while not self._shutdown_flag:
            idle_time_ms = (time.time() - self.last_activity_time) * 1000
            
            if idle_time_ms > self.config.idle_threshold_ms and not self.is_idle:
                self.is_idle = True
                self._on_idle_detected()
            elif idle_time_ms <= self.config.idle_threshold_ms and self.is_idle:
                self.is_idle = False
                
            time.sleep(0.1)

    def _start_precompute_worker(self) -> None:
        while not self._shutdown_flag:
            try:
                task = self.precompute_queue.get(timeout=1.0)
                if task is None:
                    break
                self._execute_precompute(task)
                self.precompute_queue.task_done()
            except queue.Empty:
                pass

    def _start_cache_cleaner(self) -> None:
        while not self._shutdown_flag:
            with self._cache_lock:
                now = time.time()
                keys_to_delete = []
                for k, v in self.precompute_cache.items():
                    if (now - v["created_at"]) > self.config.precompute_ttl_seconds:
                        keys_to_delete.append(k)
                        
                for k in keys_to_delete:
                    del self.precompute_cache[k]
                    
                while len(self.precompute_cache) > self.config.max_precompute_cache_size:
                    self.precompute_cache.popitem(last=False)
                    
            time.sleep(60.0)

    def _on_idle_detected(self) -> None:
        recent = list(self.conversation_history)[-5:]
        if not recent:
            return
            
        predictions = self._predict_followups(recent)
        queued = 0
        
        for pred_query, confidence in predictions:
            if confidence > self.config.prediction_confidence_threshold:
                # Check QSM cache
                if self.qsm.contains(pred_query):
                    continue
                    
                # Check local precompute cache
                cache_key = FastHashEngine.sha256_short(pred_query)
                with self._cache_lock:
                    if cache_key in self.precompute_cache:
                        continue
                        
                self.precompute_queue.put({"query": pred_query, "confidence": confidence})
                queued += 1
                
        if queued > 0:
            self.logger.info(f"Idle detected. Queued {queued} precompute tasks.")

    def _predict_followups(self, recent: List[Tuple[str, str, float]]) -> List[Tuple[str, float]]:
        last_query, last_resp, _ = recent[-1]
        topics = self._extract_topics(last_query)
        if not topics:
            return []
            
        predictions = []
        topic = topics[0]  # Take primary topic
        
        # Strategy 1: Elaboration
        elabs = [
            f"tell me more about {topic}",
            f"explain {topic} in detail",
            f"give examples of {topic}",
            f"what are the benefits of {topic}",
            f"what are the disadvantages of {topic}",
            f"how does {topic} work",
            f"why is {topic} important",
            f"history of {topic}"
        ]
        predictions.extend([(e, 0.4) for e in elabs])
        
        # Strategy 2: Comparison
        comps = [
            f"compare {topic} with alternatives",
            f"{topic} vs competitors",
            f"what is better than {topic}",
            f"pros and cons of {topic}"
        ]
        predictions.extend([(c, 0.3) for c in comps])
        
        # Strategy 3: Quantitative
        quants = [
            f"how much does {topic} cost",
            f"what is the price of {topic}",
            f"how many {topic} exist",
            f"statistics about {topic}"
        ]
        predictions.extend([(q, 0.25) for q in quants])
        
        # Strategy 4: Application
        apps = [
            f"how to use {topic}",
            f"practical applications of {topic}",
            f"{topic} in real life",
            f"implement {topic}"
        ]
        predictions.extend([(a, 0.2) for a in apps])
        
        # Strategy 5: Correction
        corrs = [
            f"is {topic} correct",
            f"problems with {topic}",
            f"limitations of {topic}",
            f"alternatives to {topic}"
        ]
        predictions.extend([(c, 0.15) for c in corrs])
        
        # Strategy 6: Contextual based on response
        if any(char.isdigit() for char in last_resp):
            predictions.append(("explain those numbers in detail", 0.35))
        if "```" in last_resp:
            predictions.append(("explain this code line by line", 0.35))
        if "1." in last_resp and "2." in last_resp:
            predictions.append(("elaborate on step 1", 0.35))
            
        # Deduplicate & Sort
        unique = {}
        for text, conf in predictions:
            if text not in unique or conf > unique[text]:
                unique[text] = conf
                
        sorted_preds = sorted(unique.items(), key=lambda x: x[1], reverse=True)
        return sorted_preds[:self.config.max_predictions_per_idle]

    def _execute_precompute(self, task: dict) -> None:
        query = task["query"]
        conf = task["confidence"]
        
        start_ms = time.perf_counter() * 1000
        try:
            if self.pse.is_loaded:
                resp, _ = self.pse.generate_with_speculation(query, max_tokens=self.config.precompute_max_tokens)
            else:
                return # Skip
        except Exception as e:
            self.logger.warning(f"Precompute failed for '{query}': {e}")
            return
            
        elapsed_ms = (time.perf_counter() * 1000) - start_ms
        cache_key = FastHashEngine.sha256_short(query)
        
        entry = {
            "query": query,
            "response": resp,
            "confidence": conf,
            "compute_time_ms": elapsed_ms,
            "created_at": time.time()
        }
        
        with self._cache_lock:
            self.precompute_cache[cache_key] = entry
            if len(self.precompute_cache) > self.config.max_precompute_cache_size:
                self.precompute_cache.popitem(last=False)
                
        self.qsm.store(query, resp, {"source": "tcs_precompute", "confidence": conf})
        
        IRALogger.log_performance("tcs", "precompute", elapsed_ms)

    def _extract_topics(self, text: str) -> List[str]:
        return TopicExtractor.extract_topics(text)

    def get_stats(self) -> dict:
        return {
            "cache_size": len(self.precompute_cache),
            "queued_tasks": self.precompute_queue.qsize(),
            "history_size": len(self.conversation_history)
        }

    def shutdown(self) -> None:
        self._shutdown_flag = True
        self.precompute_queue.put(None)
        self.idle_thread.join(timeout=2.0)
        self.worker_thread.join(timeout=2.0)
        self.cleaner_thread.join(timeout=2.0)
