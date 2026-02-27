from .embed import Embedder
from .index import RagIndex
from .retriever import Retriever
from .composer import PromptComposer
import structlog

logger = structlog.get_logger()

class RagQueryEngine:
    def __init__(self):
        self.embedder = Embedder()
        self.index = RagIndex()
        self.retriever = Retriever(self.index, self.embedder)
        self.composer = PromptComposer()
        self.cache = {}
        self.max_cache_size = 50

    def query(self, text, k=3):
        # Normalize for caching
        text_norm = " ".join(text.lower().split())
        if text_norm in self.cache:
            logger.info("rag_cache_hit", query=text_norm)
            return self.cache[text_norm]

        logger.info("rag_query_start", query=text)
        context, search_results = self.retriever.retrieve(text, k=k)
        prompt = self.composer.compose(text, context)
        
        result = {
            "query": text,
            "context": context,
            "prompt": prompt,
            "results": search_results
        }
        
        # Simple FIFO cache eviction
        if len(self.cache) >= self.max_cache_size:
            first_key = next(iter(self.cache))
            self.cache.pop(first_key)
            
        self.cache[text_norm] = result
        return result

if __name__ == "__main__":
    engine = RagQueryEngine()
    # Ensure index has something
    engine.index.add(engine.embedder.get_embeddings("HYPER is zero-hardware compute"), [{"text": "HYPER is zero-hardware compute"}])
    response = engine.query("What is HYPER?")
    print(f"RAG Prompt: {response['prompt']}")
