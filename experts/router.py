import structlog
from experts.vision_expert import VisionExpert
# Import missing experts if they exist, or mock them
try: from experts.code_expert import CodeExpert
except: CodeExpert = type('CodeExpert', (), {'run': lambda self, q: "Code output mock"})
try: from experts.text_expert import TextExpert
except: TextExpert = type('TextExpert', (), {'run': lambda self, q: "Text output mock"})
try: from experts.math_expert import MathExpert
except: MathExpert = type('MathExpert', (), {'run': lambda self, q: "Math output mock"})

logger = structlog.get_logger()

class MoERouter:
    def __init__(self):
        self.experts = {
            "code": CodeExpert(),
            "text": TextExpert(),
            "math": MathExpert(),
            "vision": VisionExpert()
        }
        # In this system, 'vision' expert handles cameras and frame sampling
        self.keywords = {
            "code": ["def", "function", "class", "import", "return", "if", "for", "{", "}", "const", "let", "var", "async", "await"],
            "math": ["+", "-", "*", "/", "sqrt", "pow", "calculate", "sum", "integral", "derivative", "equation", "log", "sin", "cos"],
            "text": ["summarize", "write", "tell", "story", "explain", "why", "how", "article", "essay", "blog", "poem"],
            "vision": ["detect", "see", "look", "image", "video", "frame", "visual", "cctv", "camera", "object", "face", "sampling", "stream"]
        }
        self.cache = {}
        self.max_cache_size = 100

    def route(self, query):
        # Normalize for semantic caching
        query_norm = " ".join(query.lower().split())
        if query_norm in self.cache:
            logger.info("cache_hit", query=query_norm)
            return self.cache[query_norm]

        logger.info("routing_query", query=query)
        query_lower = query.lower()
        
        # Weighted keyword scoring
        scores = {"code": 0, "math": 0, "text": 0, "vision": 0}
        
        for expert, phrases in self.keywords.items():
            for p in phrases:
                if p in query_lower:
                    scores[expert] += 2 # Give weight to keywords
        
        # Default to text if no strong preference
        chosen_expert = max(scores, key=scores.get)
        if scores[chosen_expert] == 0:
            chosen_expert = "text"
            
        logger.info("expert_chosen", expert=chosen_expert, scores=scores)
        
        result = {
            "query": query,
            "chosen_expert": chosen_expert,
            "scores": scores,
            "result": self.experts[chosen_expert].run(query)
        }
        
        # Simple cache eviction
        if len(self.cache) >= self.max_cache_size:
            # Pop first item (basic FIFO)
            first_key = next(iter(self.cache))
            self.cache.pop(first_key)
            
        self.cache[query_norm] = result
        return result

if __name__ == "__main__":
    router = MoERouter()
    print(router.route("def hello(): print('world')"))
    print(router.route("calculate the sum of 5 and 10"))
    print(router.route("Tell me a story about space"))
