import structlog
from .index import RagIndex
from .embed import Embedder

logger = structlog.get_logger()

class Retriever:
    def __init__(self, index: RagIndex, embedder: Embedder):
        self.index = index
        self.embedder = embedder

    def retrieve(self, query: str, k: int = 3):
        """
        Retrieves top-k context snippets for a given query.
        """
        logger.info("retrieving_context", query=query, k=k)
        query_emb = self.embedder.get_embeddings(query)
        search_results = self.index.search(query_emb, k=k)
        
        context = "\n".join([res['metadata']['text'] for res in search_results])
        return context, search_results

if __name__ == "__main__":
    # Internal test would require mock index/embedder or actual ones
    pass
