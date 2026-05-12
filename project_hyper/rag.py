import chromadb

class RetrievalEngine:
    """LAYER 2 — RETRIEVAL ENGINE (RAG)"""
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./rag_db")
        self.collection = self.client.get_or_create_collection(name="leo_knowledge")
        
    def retrieve(self, query: str, top_k: int = 3) -> str:
        results = self.collection.query(query_texts=[query], n_results=top_k)
        if not results['documents']:
            return ""
        
        # Enforce <=2K tokens roughly by limiting character count
        context = " ".join(results['documents'][0])
        return context[:8000] # ~2K tokens
