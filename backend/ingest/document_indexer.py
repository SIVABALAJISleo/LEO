import logging
from typing import List
from backend.ingest.document_loader import global_document_loader
from backend.intelligence.rag import RAGEngine

logger = logging.getLogger(__name__)

class DocumentIndexer:
    """
    Orchestrates the ingestion of documents into the RAG system and Knowledge Graph.
    """
    def __init__(self):
        self.rag = RAGEngine()

    async def index_document(self, file_path: str, workspace_id: str, tenant_id: str):
        logger.info(f"indexing_document: {file_path} [workspace={workspace_id}]")
        
        # Invalidate existing crystallized answers relying on this document
        try:
            from backend.graph.answer_graph_engine import global_age
            global_age.invalidate_by_document(file_path)
        except Exception as e:
            logger.warning(f"Failed to invalidate by document path: {e}")

        # 1. LOAD
        text = global_document_loader.load(file_path)
        
        # 2. CHUNK
        chunks = self._chunk_text(text)
        
        # 3. EMBED & INDEX (RAG)
        # We assume RAGEngine.add_documents supports metadata/tenant_id
        await self.rag.add_documents(chunks, tenant_id=tenant_id)
        
        # 4. KNOWLEDGE GRAPH EXTRACTION
        # Very simple entity relation extraction from chunks
        for chunk in chunks:
            # logic to extract nodes and relations
            # global_graph.add_relation(...)
            pass

    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        words = text.split()
        return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

global_document_indexer = DocumentIndexer()
