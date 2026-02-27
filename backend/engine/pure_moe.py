
import re

class PureMoERouter:
    """
    Pure Logic Intent Classifier & Router.
    Routes queries to experts based on heuristic analysis instead of a heavy Transformer model.
    """
    def __init__(self):
        self.expert_map = {
            "vision": ["image", "video", "frame", "render", "upscale", "pixel", "visual"],
            "logic": ["math", "compute", "calculate", "algorithm", "engine", "physics", "+", "-", "*", "/", "square", "if", "all", "some", "is", "than", "taller", "shorter", "related", "next", "implies"],
            "knowledge": ["capital", "who", "when", "where", "what", "how", "discover", "element", "history", "planet", "ocean", "mountain", "painted"],
            "data": ["database", "retrieve", "search", "context", "history", "analytics"],
            "security": ["auth", "token", "key", "login", "register", "permission"]
        }

    def route(self, query):
        query_lower = query.lower()
        scores = {expert: 0 for expert in self.expert_map}
        
        for expert, keywords in self.expert_map.items():
            for kw in keywords:
                if re.search(rf"\b{re.escape(kw)}\b", query_lower):
                    scores[expert] += 1
                    
        # Find best expert
        assigned_expert = max(scores, key=scores.get)
        if scores[assigned_expert] == 0:
            assigned_expert = "general"
            
        return {
            "query": query,
            "expert": assigned_expert,
            "confidence": 0.95 if assigned_expert != "general" else 0.5,
            "routing_logic": "HeuristicKeywordDensity",
            "subtasks": self._decompose(query, assigned_expert)
        }

    def _decompose(self, query, expert):
        # Basic decomposition logic (Pillar 1)
        subtasks = []
        if expert == "vision":
            subtasks = ["extract_regions", "low_res_compute", "perceptual_pass"]
        elif expert == "logic":
            subtasks = ["parse_expr", "approx_math", "validate_bounds"]
        else:
            subtasks = ["context_retrieval", "logic_merge"]
            
        return subtasks

if __name__ == "__main__":
    router = PureMoERouter()
    print(router.route("upscale this pixel video"))
