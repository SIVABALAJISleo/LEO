"""
phoenix/memory_manager.py
Triple Buffer Pipeline and Hot/Warm/Cold Weight Classification.
Manages extreme memory optimization for hybrid architectures.
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class WeightClassifier:
    """
    Classifies neural network layers/experts into memory tiers based on 
    access frequency and predictive profiling.
    """
    def __init__(self):
        self.access_counts: Dict[str, int] = {}
        
    def record_access(self, layer_id: str):
        self.access_counts[layer_id] = self.access_counts.get(layer_id, 0) + 1
        
    def classify_weights(self) -> Dict[str, str]:
        """
        Returns a mapping of layer_id to its optimal memory tier.
        Tiers:
        - 'HOT': Pin to iGPU VRAM or L3 Cache (most frequent)
        - 'WARM': Pin to System RAM (moderately frequent)
        - 'COLD': Leave on NVMe SSD (mmap) (rarely accessed)
        """
        if not self.access_counts:
            return {}
            
        sorted_layers = sorted(self.access_counts.items(), key=lambda x: x[1], reverse=True)
        total = len(sorted_layers)
        
        classifications = {}
        for i, (layer_id, count) in enumerate(sorted_layers):
            if i < total * 0.2:
                classifications[layer_id] = 'HOT'
            elif i < total * 0.6:
                classifications[layer_id] = 'WARM'
            else:
                classifications[layer_id] = 'COLD'
                
        return classifications

class TripleBufferPipeline:
    """
    Triple Buffering for LLM inference.
    Buffer 0: Executing on iGPU
    Buffer 1: Transferring to iGPU (Prefetch)
    Buffer 2: Loading from SSD (mmap) -> RAM
    """
    def __init__(self):
        self.buffers = [None, None, None]
        self.classifier = WeightClassifier()
        
    def step_pipeline(self, next_layer_id: str):
        """
        Advances the buffer states. 
        In a real implementation, this triggers async DMA transfers.
        """
        self.classifier.record_access(next_layer_id)
        
        # Shift buffers
        executing = self.buffers[1]
        transferring = self.buffers[2]
        loading = next_layer_id
        
        self.buffers[0] = executing
        self.buffers[1] = transferring
        self.buffers[2] = loading
        
        if executing:
            logger.debug(f"[Pipeline] Executing: {executing}")
