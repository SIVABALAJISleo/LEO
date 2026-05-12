"""
backend/graph/query_graph.py

Query Graph System (AIS++ Module 2)
=====================================
Nodes = queries (family_ids)
Edges = semantic relationships (similarity, follow-up, prerequisite, comparison)

Instead of resolving queries one-at-a-time, solves GRAPH CLUSTERS —
if we know any node in a cluster, we can infer/compose related nodes.

Caches entire subgraphs for reuse.
Self-expanding: new queries automatically connect to existing nodes.

Rules:
  - Every new answer registers as a node
  - Edges drawn based on entity/intent overlap and semantic similarity
  - Subgraph cache invalidated only when root node changes
  - Zero-recompute: graph traversal never calls model
"""
import logging
import time
import json
import os
import hashlib
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

GRAPH_STORE_PATH = os.path.join(os.getcwd(), "data", "query_graph.json")
EDGE_SIMILARITY_THRESHOLD = 0.70   # min similarity to draw an edge
MAX_CLUSTER_SIZE = 25              # limit traversal depth


class QueryNode:
    """A single query node in the graph."""
    __slots__ = ["family_id", "query", "answer", "entity", "intent",
                 "confidence", "timestamp", "hits", "edges"]

    def __init__(
        self,
        family_id: str,
        query: str,
        answer: str,
        entity: str,
        intent: str,
        confidence: float,
    ):
        self.family_id  = family_id
        self.query      = query
        self.answer     = answer
        self.entity     = entity
        self.intent     = intent
        self.confidence = confidence
        self.timestamp  = time.time()
        self.hits       = 0
        self.edges: Set[str] = set()   # set of connected family_ids

    def to_dict(self) -> Dict[str, Any]:
        return {
            "family_id":  self.family_id,
            "query":      self.query,
            "answer":     self.answer,
            "entity":     self.entity,
            "intent":     self.intent,
            "confidence": self.confidence,
            "timestamp":  self.timestamp,
            "hits":       self.hits,
            "edges":      list(self.edges),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "QueryNode":
        n = cls(
            d["family_id"], d["query"], d["answer"],
            d["entity"], d["intent"], d["confidence"]
        )
        n.timestamp = d.get("timestamp", time.time())
        n.hits      = d.get("hits", 0)
        n.edges     = set(d.get("edges", []))
        return n


class QueryGraphSystem:
    """
    Semantic query graph.
    Enables cluster-level compute avoidance — one answer seeds many related queries.
    """

    def __init__(self):
        self._nodes: Dict[str, QueryNode] = {}     # family_id → node
        self._entity_index: Dict[str, Set[str]] = defaultdict(set)   # entity → family_ids
        self._intent_index: Dict[str, Set[str]] = defaultdict(set)   # intent → family_ids
        self._subgraph_cache: Dict[str, List[str]] = {}               # root_id → cluster ids
        self._load()

    # ── Node Registration ─────────────────────────────────────────────────── #

    def register(
        self,
        family_id: str,
        query: str,
        answer: str,
        entity: str,
        intent: str,
        confidence: float,
    ) -> None:
        """
        Adds a query+answer as a node in the graph.
        Automatically draws edges to related existing nodes.
        """
        if family_id in self._nodes:
            # Update existing node
            node = self._nodes[family_id]
            if confidence > node.confidence:
                node.answer = answer
                node.confidence = confidence
            node.hits += 1
            self._save_async()
            return

        node = QueryNode(family_id, query, answer, entity, intent, confidence)
        self._nodes[family_id] = node

        # Index by entity and intent
        self._entity_index[entity.upper()].add(family_id)
        self._intent_index[intent].add(family_id)

        # Draw edges to related nodes
        self._draw_edges(node)

        self._save_async()
        logger.debug(f"graph.register: family={family_id} entity={entity} intent={intent}")

    # ── Lookup ────────────────────────────────────────────────────────────── #

    def lookup(self, family_id: str) -> Optional[Dict[str, Any]]:
        """Exact node lookup by family_id."""
        node = self._nodes.get(family_id)
        if node:
            node.hits += 1
            return {"answer": node.answer, "confidence": node.confidence,
                    "entity": node.entity, "intent": node.intent, "hits": node.hits}
        return None

    def lookup_by_entity_intent(
        self, entity: str, intent: str
    ) -> Optional[Dict[str, Any]]:
        """
        Finds the best answer for entity+intent across all nodes.
        Used when exact family_id is unavailable.
        """
        candidates = self._entity_index.get(entity.upper(), set()) & \
                     self._intent_index.get(intent, set())
        if not candidates:
            # Relax to entity-only
            candidates = self._entity_index.get(entity.upper(), set())
        if not candidates:
            return None

        # Best by confidence × hits
        best = max(
            candidates,
            key=lambda fid: self._nodes[fid].confidence * (1 + self._nodes[fid].hits * 0.01),
            default=None,
        )
        if best:
            node = self._nodes[best]
            node.hits += 1
            logger.info(f"graph.entity_intent_hit: entity={entity} intent={intent} fid={best}")
            return {"answer": node.answer, "confidence": node.confidence,
                    "family_id": best, "source": "query_graph"}
        return None

    # ── Cluster / Subgraph ────────────────────────────────────────────────── #

    def get_cluster(self, family_id: str) -> List[Dict[str, Any]]:
        """
        BFS traversal to get all nodes in the same cluster.
        Returns list of node dicts.
        Uses subgraph cache to avoid re-traversal.
        """
        if family_id in self._subgraph_cache:
            cluster_ids = self._subgraph_cache[family_id]
            return [self._nodes[fid].to_dict() for fid in cluster_ids if fid in self._nodes]

        if family_id not in self._nodes:
            return []

        visited: Set[str] = set()
        queue: deque = deque([family_id])
        cluster: List[str] = []

        while queue and len(cluster) < MAX_CLUSTER_SIZE:
            fid = queue.popleft()
            if fid in visited:
                continue
            visited.add(fid)
            cluster.append(fid)
            if fid in self._nodes:
                for neighbor in self._nodes[fid].edges:
                    if neighbor not in visited:
                        queue.append(neighbor)

        self._subgraph_cache[family_id] = cluster
        logger.debug(f"graph.cluster: root={family_id} size={len(cluster)}")
        return [self._nodes[fid].to_dict() for fid in cluster if fid in self._nodes]

    def compose_cluster_answer(self, family_id: str, query: str) -> Optional[str]:
        """
        Attempts to compose an answer from the cluster without model call.
        Finds the closest node in the cluster to the given query.
        """
        cluster = self.get_cluster(family_id)
        if not cluster:
            return None

        # Pick highest confidence node in cluster
        best = max(cluster, key=lambda n: n["confidence"], default=None)
        if best and best["confidence"] >= 0.88:
            logger.info(f"graph.cluster_compose: root={family_id} best_conf={best['confidence']:.3f}")
            return best["answer"]
        return None

    # ── Gap Detection ─────────────────────────────────────────────────────── #

    def find_missing_nodes(self, entity: str) -> List[str]:
        """
        Identifies which intent types lack coverage for the given entity.
        Returns list of queries to precompute.
        """
        covered_intents = set()
        for fid in self._entity_index.get(entity.upper(), set()):
            node = self._nodes.get(fid)
            if node:
                covered_intents.add(node.intent)

        all_intents = {"definition", "how_to", "comparison", "benefit", "troubleshoot", "calculation"}
        missing = all_intents - covered_intents

        missing_queries = []
        for intent in missing:
            templates = {
                "definition":   f"What is {entity.lower()}?",
                "how_to":       f"How to use {entity.lower()}?",
                "comparison":   f"{entity.lower()} vs alternatives",
                "benefit":      f"Benefits of {entity.lower()}",
                "troubleshoot": f"Common {entity.lower()} errors",
                "calculation":  f"How to calculate {entity.lower()} metrics",
            }
            missing_queries.append(templates[intent])

        if missing_queries:
            logger.debug(f"graph.gaps: entity={entity} missing={missing}")
        return missing_queries

    def stats(self) -> Dict[str, Any]:
        total_edges = sum(len(n.edges) for n in self._nodes.values())
        return {
            "total_nodes": len(self._nodes),
            "total_edges": total_edges,
            "unique_entities": len(self._entity_index),
            "unique_intents": len(self._intent_index),
            "subgraph_cache_size": len(self._subgraph_cache),
        }

    # ── Internal ──────────────────────────────────────────────────────────── #

    def _draw_edges(self, new_node: QueryNode) -> None:
        """Connects the new node to related existing nodes."""
        # Same entity + different intent → edge (follow-up relationship)
        for fid in self._entity_index.get(new_node.entity.upper(), set()):
            if fid == new_node.family_id:
                continue
            existing = self._nodes.get(fid)
            if existing:
                new_node.edges.add(fid)
                existing.edges.add(new_node.family_id)
                # Invalidate subgraph cache for affected nodes
                self._subgraph_cache.pop(fid, None)

        # Same intent + different entity → edge (comparison/pattern relationship)
        for fid in list(self._intent_index.get(new_node.intent, set()))[:5]:
            if fid == new_node.family_id or fid in new_node.edges:
                continue
            new_node.edges.add(fid)

    def _save_async(self) -> None:
        """Fire-and-forget persistence."""
        try:
            import threading
            threading.Thread(target=self._save, daemon=True).start()
        except Exception:
            pass

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(GRAPH_STORE_PATH), exist_ok=True)
            data = {fid: node.to_dict() for fid, node in self._nodes.items()}
            with open(GRAPH_STORE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception as exc:
            logger.warning(f"graph.save_error: {exc}")

    def _load(self) -> None:
        if not os.path.exists(GRAPH_STORE_PATH):
            return
        try:
            with open(GRAPH_STORE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            for fid, d in data.items():
                node = QueryNode.from_dict(d)
                self._nodes[fid] = node
                self._entity_index[node.entity.upper()].add(fid)
                self._intent_index[node.intent].add(fid)
            logger.info(f"graph.loaded: nodes={len(self._nodes)}")
        except Exception as exc:
            logger.warning(f"graph.load_error: {exc}")


global_query_graph = QueryGraphSystem()
