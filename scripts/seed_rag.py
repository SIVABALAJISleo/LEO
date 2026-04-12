import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from backend.intelligence.rag import RAGEngine

async def seed():
    print("Seeding RAG Engine with real documents...")
    rag = RAGEngine()
    
    documents = [
        "Project HYPER is a next-generation AI platform focused on compute avoidance and zero-runtime stability.",
        "The system uses a 12-module architecture including Global Memory, Fragment Graph Composition, and Chaos Control.",
        "Latency is strictly enforced below 50ms using a multi-layer caching and predictive execution system.",
        "Nvidia inspired design principles are used throughout the frontend to provide a premium user experience.",
        "The backend is built with FastAPI and uses llama.cpp for local CPU-optimized inference.",
        "Compute avoidance is achieved by reusing previously generated answers stored in the Semantic Canonical Answer Reuse layer.",
        "The Chaos Controller monitors system resources and switches to MINIMAL mode under extreme stress.",
        "Sentence Transformers are used to generate embeddings for semantic similarity search in the FAISS index.",
        "Project LEO is the codename for the hardened, production-ready version of the HYPER platform.",
        "Digital Twin reasoning allows the system to simulate outcomes and bypass heavy LLM calls for known patterns."
    ]
    
    await rag.add_documents(documents, tenant_id="default")
    print(f"Successfully indexed {len(documents)} documents.")
    
    from backend.graph.fragment_graph import global_fragment_graph
    print("Seeding Fragment Graph...")
    global_fragment_graph.register_fragment("HYPER", "definition", "Project HYPER is a next-generation AI platform focused on compute avoidance.")
    global_fragment_graph.register_fragment("HYPER", "mission", "The mission is to achieve practical GPU irrelevance via zero-runtime compute.")
    global_fragment_graph.register_fragment("LEO", "info", "Project LEO is the production-ready implementation of the HYPER architecture.")
    print("Fragment Graph seeded.")
    
    # Verify similarity
    print("\nVerifying similarity...")
    query = "What is Project HYPER?"
    results = rag.retrieve(query, tenant_id="default", k=2)
    
    for i, res in enumerate(results):
        print(f"Result {i+1}: {res['content'][:50]}... (Score: {res['score']:.4f})")
        if res['score'] <= 0.0:
            print("WARNING: Similarity score is 0.0 or less!")
        else:
            print("SUCCESS: Non-zero similarity detected.")

if __name__ == "__main__":
    asyncio.run(seed())
