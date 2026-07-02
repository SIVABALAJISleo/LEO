from .embed import Embedder
from .index import RagIndex
from .retriever import Retriever
from .composer import PromptComposer
from core_ai.fabric.topological_hypergraph import TopologicalHypergraph
from core_ai.fabric.delta_reality_engine import DeltaRealityEngine
import structlog

logger = structlog.get_logger()

class RagQueryEngine:
    def __init__(self):
        self.embedder = Embedder()
        self.index = RagIndex()
        self.retriever = Retriever(self.index, self.embedder)
        self.composer = PromptComposer()
        self.hypergraph = TopologicalHypergraph()
        self.delta_engine = DeltaRealityEngine()
        self.cache = {}
        self.max_cache_size = 50

    def query(self, text, k=3):
        # 1. Topological Hypergraph First for Instant Multi-hop Reasoning
        holographic_sig = text.encode('utf-8')
        recon = self.hypergraph.reconstruct_from_interference(holographic_sig)
        if recon and recon.get("confidence", 0) > 0.99:
            logger.info("topological_hypergraph_hit", query=text)
            return {
                "query": text,
                "context": "Topological Hypergraph Reconstruction",
                "prompt": recon["reconstructed_data"],
                "results": []
            }

        # 2. Delta-only Verification & Prediction Bypass
        predicted_dream = self.delta_engine.dream_probable_outcome(text)
        delta_status = self.delta_engine.verify_delta(predicted_dream, text)
        if delta_status.get("status") == "verified":
            logger.info("delta_prediction_bypass", query=text)
            return {
                "query": text,
                "context": "Delta Synthesis Dream",
                "prompt": f"Synthesized: {predicted_dream}",
                "results": []
            }

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
