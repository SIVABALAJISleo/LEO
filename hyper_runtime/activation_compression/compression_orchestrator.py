import logging
import numpy as np

from .entropy_compressor import EntropyActivationCompressor
from .ssd_pager import SSDActivationPager
from .recomputation_engine import RecomputationEngine

logger = logging.getLogger("HyperCore.CompressionOrchestrator")

class ActivationCompressionEngine:
    """
    HyperCore MODULE 9 — Activation Compression Engine
    
    Dynamically decides whether to:
    1. Compress activations in RAM (FP16 critical + INT8 low-var).
    2. Page out compressed activations to SSD if RAM is under pressure.
    3. Discard entirely and use procedural recomputation.
    """
    def __init__(self, ram_pressure_threshold: float = 0.85):
        self.compressor = EntropyActivationCompressor(variance_threshold=0.05, quantization_bits=8)
        self.pager = SSDActivationPager()
        self.recompute_engine = RecomputationEngine()
        self.ram_pressure_threshold = ram_pressure_threshold
        
    def store_activations(self, layer_id: str, activations: np.ndarray, current_ram_usage: float) -> dict:
        """
        Takes raw fp32 activations and dynamically stores them based on memory pressure.
        """
        # Compress first
        payload, metrics = self.compressor.compress(activations)
        
        storage_tier = "RAM_COMPRESSED"
        page_id = None
        
        # If RAM is critical, page it out
        if current_ram_usage > self.ram_pressure_threshold:
            page_id = self.pager.page_out(payload)
            storage_tier = "SSD_PAGED"
            payload = None # Clear from RAM
            
        return {
            "layer_id": layer_id,
            "storage_tier": storage_tier,
            "payload": payload,
            "page_id": page_id,
            "metrics": metrics
        }
        
    def retrieve_activations(self, store_handle: dict) -> np.ndarray:
        """
        Retrieves and reconstructs activations from RAM or SSD.
        """
        tier = store_handle["storage_tier"]
        
        if tier == "RAM_COMPRESSED":
            payload = store_handle["payload"]
        elif tier == "SSD_PAGED":
            payload = self.pager.page_in(store_handle["page_id"])
        else:
            raise ValueError(f"Unknown storage tier: {tier}")
            
        reconstructed = self.compressor.decompress(payload)
        return reconstructed
