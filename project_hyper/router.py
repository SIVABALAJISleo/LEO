
class QueryRouter:
    """LAYER 1 — QUERY ROUTER"""
    def __init__(self):
        self.tool_keywords = ['calculate', 'solve', 'math', 'equation']
        self.code_keywords = ['python', 'script', 'function', 'def ']
        self.reasoning_keywords = ['why', 'explain', 'compare', 'analyze']
        
    def classify(self, query: str) -> str:
        q = query.lower()
        if any(k in q for k in self.tool_keywords):
            return "high-precision"
        elif any(k in q for k in self.code_keywords):
            return "high-precision"
        elif any(k in q for k in self.reasoning_keywords):
            return "reasoning"
        elif len(q.split()) > 15:
            return "retrieval-based"
        return "simple"
