import json
import logging
from typing import Dict, Any, List
from backend.core.database import SessionLocal, CompressedKnowledge, CompressedFragment

logger = logging.getLogger(__name__)

class StorageOptimizer:
    """
    Ensures that ONLY compressed knowledge and Fragment IDs are stored in the persistent database.
    Intercepts raw string storage and replaces it with structured compression.
    """
    
    def store_compressed(self, canonical_id: str, compressed_data: Dict[str, Any], fragment_ids: List[str], tenant_id: str = "default"):
        """Saves minimal representation with pointers to fragments in the DB."""
        db = SessionLocal()
        try:
            # 1. Store Fragments
            for fid in fragment_ids:
                # In a real system, we'd check if fragment exists first
                # For fragments.py, we'd need to get the actual text back to store it here
                # Assuming fragment_optimizer/compressor handles the text-to-ID mapping
                pass

            # 2. Store Knowledge
            knowledge = db.query(CompressedKnowledge).filter(CompressedKnowledge.id == canonical_id).first()
            if not knowledge:
                knowledge = CompressedKnowledge(
                    id=canonical_id,
                    concept=compressed_data.get("concept"),
                    intent=compressed_data.get("intent"),
                    key_points_json=json.dumps(compressed_data.get("key_points", [])),
                    fragment_ids_json=json.dumps(fragment_ids),
                    tenant_id=tenant_id
                )
                db.add(knowledge)
            else:
                knowledge.key_points_json = json.dumps(compressed_data.get("key_points", []))
                knowledge.fragment_ids_json = json.dumps(fragment_ids)
            
            db.commit()
            logger.info(f"storage_optimized: Persisted canonical_id={canonical_id} to database.")
        except Exception as e:
            logger.error(f"storage_persistence_failed: {e}")
            db.rollback()
        finally:
            db.close()

    def retrieve(self, canonical_id: str) -> Dict[str, Any]:
        """Fetches compressed info from the DB to feed to the Reconstructor."""
        db = SessionLocal()
        try:
            knowledge = db.query(CompressedKnowledge).filter(CompressedKnowledge.id == canonical_id).first()
            if knowledge:
                return {
                    "compressed_data": {
                        "concept": knowledge.concept,
                        "intent": knowledge.intent,
                        "key_points": json.loads(knowledge.key_points_json)
                    },
                    "fragments": json.loads(knowledge.fragment_ids_json)
                }
        finally:
            db.close()
        return None

global_storage_optimizer = StorageOptimizer()
