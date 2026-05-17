import os
import uuid
import numpy as np
import logging
import pickle

logger = logging.getLogger("HyperCore.SSDPager")

class SSDActivationPager:
    """
    Pages out compressed activation tensors to NVMe/SSD to prevent RAM OOMs
    during long-context reasoning or heavy inference batches.
    """
    def __init__(self, page_dir: str = ".hyper_cache/pagefile"):
        self.page_dir = page_dir
        os.makedirs(self.page_dir, exist_ok=True)
        self.page_map = {} # page_id -> filepath
        
    def page_out(self, payload: dict) -> str:
        """
        Serializes and writes payload to SSD.
        Returns a page ID.
        """
        page_id = str(uuid.uuid4())
        filepath = os.path.join(self.page_dir, f"{page_id}.page")
        
        # Serialize to disk (in a real system, use memmap or specialized formats)
        with open(filepath, 'wb') as f:
            pickle.dump(payload, f)
            
        self.page_map[page_id] = filepath
        logger.debug(f"Paged out activation {page_id} to SSD.")
        return page_id
        
    def page_in(self, page_id: str) -> dict:
        """
        Reads payload from SSD back into RAM and deletes the pagefile.
        """
        if page_id not in self.page_map:
            raise KeyError(f"Page ID {page_id} not found in swap.")
            
        filepath = self.page_map[page_id]
        
        with open(filepath, 'rb') as f:
            payload = pickle.load(f)
            
        # Clean up
        try:
            os.remove(filepath)
            del self.page_map[page_id]
        except Exception as e:
            logger.warning(f"Failed to clean up page file {filepath}: {e}")
            
        return payload
