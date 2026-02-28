"""
Autonomous Memory & Retrieval Layer
Uses LlamaIndex + ChromaDB.
Builds an embedded vector index of the current project, allowing the autonomous 
agent to ask "Where is the API routing bug?" and instantly load file context.
"""

import os
import logging
from typing import List

# LlamaIndex & Chroma dependencies
import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

logger = logging.getLogger(__name__)

class ProjectMemoryStore:
    """
    Manages embedding the raw codebase into a searchable vector database.
    """
    
    def __init__(self, db_path: str = "./hyper_production.db/chroma_storage"):
        """Initialize local Chroma client and LlamaIndex settings."""
        self.db_path = db_path
        os.makedirs(db_path, exist_ok=True)
        
        logger.info(f"Initializing Memory Store at {self.db_path}")
        
        # 1. Setup ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=self.db_path)
        self.chroma_collection = self.chroma_client.get_or_create_collection("hyper_codebase")
        
        # 2. Bind Chroma to LlamaIndex
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        
        # 3. Setup lightweight local embedding model (runs purely on CPU)
        # Using a fast embedding model optimal for code snippets
        self.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        Settings.embed_model = self.embed_model
        
        # We nullify the global LLM since we inject our Llama.cpp engine later during actual queries
        Settings.llm = None  
        
        self.index = None

    def index_project_directory(self, target_dir: str):
        """Scans the directory, chunks code files, and embeddings them into ChromaDB."""
        logger.info(f"[Memory] Scanning directory for RAG embedding: {target_dir}")
        if not os.path.exists(target_dir):
            logger.error(f"Directory {target_dir} does not exist.")
            return False
            
        try:
            # We ignore environments and node_modules
            def file_filter(file_name: str) -> bool:
                if any(ignored in file_name for ignored in ['node_modules', 'venv', '.git', '__pycache__', '.pytest_cache']):
                    return False
                return file_name.endswith(('.py', '.ts', '.tsx', '.md', '.json'))
                
            reader = SimpleDirectoryReader(
                input_dir=target_dir,
                recursive=True,
                file_extractor=None, # use default text extractors
            )
            
            # Manually filter
            files = reader.list_resources()
            valid_files = [f for f in files if file_filter(str(f))]
            
            logger.info(f"Loading {len(valid_files)} source files...")
            
            # Recreate reader with specific files
            if not valid_files:
                logger.warning("No valid files found to index.")
                return False
                
            filtered_reader = SimpleDirectoryReader(input_files=valid_files)
            documents = filtered_reader.load_data()
            
            # Embed and Index
            self.index = VectorStoreIndex.from_documents(
                documents, 
                storage_context=self.storage_context
            )
            logger.info("[Memory] Codebase indexing complete and persisted.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index project: {e}")
            return False

    def query_codebase(self, query_string: str) -> str:
        """Allows the agent to ask questions against the codebase."""
        if not self.index:
            # If we already have the DB populated, just load it
            try:
                self.index = VectorStoreIndex.from_vector_store(
                    self.vector_store,
                    embed_model=self.embed_model
                )
            except Exception as e:
                logger.error(f"Cannot query, index missing. {e}")
                return "Error: Codebase memory index is empty."
                
        # Since Settings.llm is None, we use a VectorIndexRetriever instead of a full QueryEngine
        # We just want the context chunks, the agent's brain will do the actual parsing
        try:
            retriever = self.index.as_retriever(similarity_top_k=3)
            nodes = retriever.retrieve(query_string)
            
            if not nodes:
                return "No relevant code context found."
                
            context = "\n---\n".join([
                f"File: {n.node.metadata.get('file_name', 'Unknown')}\nContext:\n{n.node.get_text()}" 
                for n in nodes
            ])
            return context
            
        except Exception as e:
             return f"RAG Query Failed: {e}"
