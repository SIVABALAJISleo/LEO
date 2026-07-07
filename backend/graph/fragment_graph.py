import logging
import json
import os
from typing import Dict

logger = logging.getLogger(__name__)

GRAPH_PATH = os.path.join(os.getcwd(), "data", "fragment_graph.json")

class FragmentGraph:
    """
    Knowledge Composition Graph.
    Stores reusable fragments of intelligence indexed by entity and type.
    Enables dynamic assembly of answers.
    """
    def __init__(self):
        self.nodes: Dict[str, Dict[str, str]] = {} # entity -> {fragment_type: content}
        self._ensure_data_dir()
        self.load()

    def _ensure_data_dir(self):
        os.makedirs(os.path.dirname(GRAPH_PATH), exist_ok=True)

    def register_fragment(self, entity: str, fragment_type: str, content: str):
        entity = entity.upper()
        if entity not in self.nodes:
            self.nodes[entity] = {}
        self.nodes[entity][fragment_type] = content
        self.save()

    def get_fragments(self, entity: str) -> Dict[str, str]:
        return self.nodes.get(entity.upper(), {})

    def save(self):
        try:
            with open(GRAPH_PATH, "w") as f:
                json.dump(self.nodes, f)
        except Exception as e:
            logger.error(f"fragment_graph_save_failed: {e}")

    def load(self):
        if os.path.exists(GRAPH_PATH):
            try:
                with open(GRAPH_PATH, "r") as f:
                    self.nodes = json.load(f)
                logger.info(f"fragment_graph_loaded: entities={len(self.nodes)}")
            except Exception as e:
                logger.error(f"fragment_graph_load_failed: {e}")

global_fragment_graph = FragmentGraph()
