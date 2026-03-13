from rag.embed import Embedder
from rag.index import RagIndex
import os

def seed():
    embedder = Embedder()
    index = RagIndex()
    
    documents = [
        "NVIDIA Blackwell architecture provides 25x better energy efficiency than previous generations.",
        "The HYPER GPU-Irrelevance engine allows running LLMs on CPU by using MoE and RAG software patterns.",
        "Sparse Mixture of Experts (MoE) only activates a fraction of the total parameters for each query, reducing compute load.",
        "Neural upscaling using Real-ESRGAN can restore high-fidelity textures on integrated GPUs."
    ]
    
    embeddings = embedder.get_embeddings(documents)
    index.add(embeddings, [{"text": doc} for doc in documents])
    print(f"Successfully seeded RAG index with {len(documents)} documents.")

if __name__ == "__main__":
    seed()
