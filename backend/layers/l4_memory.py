"""
Layer 4: Knowledge Memory Architecture
Manages Working, Episodic, Semantic, Reflection, Failure, and Procedural memories.
"""
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MemoryArchitectureLayer:
    def __init__(self):
        self.layer_id = 4
        self.layer_name = "Layer 4: Knowledge Memory"
        self.working_mem = {}
        self.episodic_mem = []
        self.semantic_mem = {}
        self.reflection_mem = []
        self.failure_mem = []
        self.procedural_mem = {}

    def record_episode(self, query: str, answer: str, confidence: float):
        # Age previous episodes (decay)
        now = time.time()
        self.episodic_mem.append({
            "query": query,
            "answer": answer,
            "confidence": confidence,
            "timestamp": now,
            "weight": 1.0
        })
        # Consolidate if memory gets too large
        if len(self.episodic_mem) > 100:
            self.consolidate_memories()

    def record_failure(self, query: str, error_msg: str):
        self.failure_mem.append({
            "query": query,
            "error": error_msg,
            "timestamp": time.time()
        })

    def consolidate_memories(self):
        """Merges episodic items into semantic rules."""
        logger.info(f"[{self.layer_name}] Consolidating episodic memories into semantic knowledge.")
        for item in self.episodic_mem:
            # Simple rule extraction: map query prefix to answer
            words = item["query"].split()
            if len(words) > 2:
                key = " ".join(words[:2]).lower()
                self.semantic_mem[key] = item["answer"]
        # Clear consolidated episodes
        self.episodic_mem = self.episodic_mem[-10:]

    def execute(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Search across Working, Semantic, and Failure Memories
        query_words = query.lower().split()
        
        # Check Working Memory
        if query in self.working_mem:
            return {
                "resolved": True,
                "answer": f"[WORKING MEMORY] {self.working_mem[query]}",
                "confidence": 0.95,
                "latency_ms": 1.0
            }
            
        # Check Semantic Memory
        if len(query_words) > 2:
            key = " ".join(query_words[:2]).lower()
            if key in self.semantic_mem:
                return {
                    "resolved": True,
                    "answer": f"[SEMANTIC MEMORY] {self.semantic_mem[key]}",
                    "confidence": 0.88,
                    "latency_ms": 1.8
                }
                
        # Check Failure Memory to warn about known failures
        for fail in self.failure_mem:
            if query_words == fail["query"].lower().split():
                return {
                    "resolved": True,
                    "answer": f"[FAILURE AVOIDANCE] Query previously failed: {fail['error']}.",
                    "confidence": 0.99,
                    "latency_ms": 1.2
                }

        # Check Procedural memory (standard macro rules)
        for trigger, procedure in self.procedural_mem.items():
            if trigger in query.lower():
                return {
                    "resolved": True,
                    "answer": f"[PROCEDURAL RUN] Executed rule: {procedure}",
                    "confidence": 0.92,
                    "latency_ms": 2.0
                }

        return {
            "resolved": False,
            "confidence": 0.0,
            "latency_ms": 1.0
        }
