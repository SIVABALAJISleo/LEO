import faiss
import numpy as np
import pickle # nosec B403
import json
import os
import logging
from typing import Optional, Dict, List, Any
from backend.core.database import SessionLocal, QueryCluster

logger = logging.getLogger(__name__)

class SemanticCanonicalEngine:
    """
    Upgraded Canonical Engine using FAISS for semantic clustering.
    Maps similar queries to the same 'canonical_id' to ensure compute-once behavior.
    """
    def __init__(self, dimension: int = 384, db_path: str = "data/canonical_faiss.bin"):
        self.dimension = dimension
        self.db_path = db_path
        self.metadata_path = db_path.replace(".bin", "_meta.json")
        self.index = faiss.IndexFlatL2(dimension)
        self.ids: List[int] = [] # List of QueryCluster.id
        
        # Load existing index if available
        if os.path.exists(self.db_path):
            try:
                self.index = faiss.read_index(self.db_path)
                if os.path.exists(self.metadata_path):
                    with open(self.metadata_path, "rb") as f:
                        self.ids = pickle.load(f) # nosec B301 - trusted internal file only
                elif os.path.exists(self.metadata_path.replace(".json", ".pkl")):
                    # Migration: try to load old pickle if present (Safe since we created it locally)
                    import pickle # nosec B403
                    with open(self.metadata_path.replace(".json", ".pkl"), "rb") as f:
                        self.ids = pickle.load(f) # nosec
                logger.info(f"SemanticCanonicalEngine: Loaded {len(self.ids)} clusters")
            except Exception as e:
                logger.error(f"SemanticCanonicalEngine: Load error {e}")

    def lookup(self, query_emb: np.ndarray, threshold: float = 0.5) -> Optional[Dict[str, Any]]:
        """
        Finds the nearest canonical cluster for the given embedding.
        Threshold 0.5 for L2 distance (Calibrated for all-MiniLM-L6-v2).
        """
        if self.index.ntotal == 0:
            return None

        # Ensure correct shape
        emb = query_emb.astype("float32").reshape(1, -1)
        distances, indices = self.index.search(emb, 1)
        
        dist = distances[0][0]
        idx = indices[0][0]
        
        # L2 distance < 0.5 is very similar for normalized MiniLM embeddings
        if idx != -1 and dist < threshold:
            cluster_id = self.ids[idx]
            db = SessionLocal()
            try:
                from backend.core.database import QueryCluster
                cluster = db.query(QueryCluster).get(cluster_id)
                if cluster:
                    cluster.use_count += 1
                    db.commit()
                    return {
                        "answer": cluster.canonical_answer,
                        "confidence": 1.0 - (dist / threshold * 0.3), # High confidence for hits
                        "canonical": True,
                        "cluster_id": cluster.id
                    }
            finally:
                db.close()
        return None

    def register(self, query: str, answer: str, embedding: np.ndarray, tenant_id: str):
        """Registers a new high-confidence answer as a canonical cluster."""
        db = SessionLocal()
        try:
            # 1. Store in SQL
            import hashlib
            h = hashlib.sha256(query.lower().strip().encode()).hexdigest()
            
            new_c = QueryCluster(
                cluster_hash=h,
                canonical_query=query,
                canonical_answer=answer,
                embedding=embedding.tobytes(),
                tenant_id=tenant_id
            )
            db.add(new_c)
            db.commit()
            db.refresh(new_c)
            
            # 2. Add to FAISS
            self.index.add(embedding.astype("float32").reshape(1, -1))
            self.ids.append(new_c.id)
            
            # 3. Persist FAISS
            faiss.write_index(self.index, self.db_path)
            with open(self.metadata_path.replace(".json", ".pkl"), "wb") as f:
                pickle.dump(self.ids, f)
                
            logger.info(f"SemanticCanonicalEngine: Registered new cluster {new_c.id}")
        except Exception as e:
            logger.error(f"SemanticCanonicalEngine: Register error {e}")
            db.rollback()
        finally:
            db.close()

global_semantic_canonical = SemanticCanonicalEngine()
