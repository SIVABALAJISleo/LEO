import json
import os
from typing import Optional

class PrecomputedReasoningGraph:
    """
    Layer 9: Precomputed Reasoning Graph
    Decision trees and stored reasoning paths.
    Runtime = lookup, not thinking.
    """
    def __init__(self, graph_path: str = "project_hyper/data/reasoning_graph.json"):
        self.graph_path = graph_path
        self.graph = {}
        self._load_graph()

    def _load_graph(self):
        if os.path.exists(self.graph_path):
            try:
                with open(self.graph_path, "r") as f:
                    self.graph = json.load(f)
            except json.JSONDecodeError:
                self.graph = {}
        else:
            # Mock initial graph
            self.graph = {
                "troubleshoot_network": {
                    "step_1": "Check physical connection.",
                    "step_2": "Verify IP configuration (DHCP vs Static).",
                    "step_3": "Ping gateway and DNS."
                }
            }

    def traverse(self, intent_key: str) -> Optional[str]:
        """Looks up a precomputed reasoning path based on intent."""
        path = self.graph.get(intent_key)
        if path:
            return "\\n".join([f"{k}: {v}" for k, v in path.items()])
        return None

if __name__ == "__main__":
    graph = PrecomputedReasoningGraph()
    print(graph.traverse("troubleshoot_network"))
