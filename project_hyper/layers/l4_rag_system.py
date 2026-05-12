import chromadb
from typing import List

class RAGSystem:
    """
    Layer 4: RAG System
    Retrieval Augmented Generation using CPU-based embeddings.
    """
    def __init__(self, collection_name: str = "leo_docs"):
        self.client = chromadb.PersistentClient(path="project_hyper/data/chroma_db")
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_docs(self, docs: List[str], ids: List[str]):
        self.collection.add(documents=docs, ids=ids)

    def retrieve(self, query: str, top_k: int = 3) -> str:
        results = self.collection.query(query_texts=[query], n_results=top_k)
        if results['documents']:
            return "\n".join(results['documents'][0])
        return ""

if __name__ == "__main__":
    rag = RAGSystem()
    rag.add_docs(["PROJECT HYPER is a zero-gpu system.", "Layer 4 is RAG."], ["1", "2"])
    print(rag.retrieve("What is project leo?"))
