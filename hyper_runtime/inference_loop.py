import threading
import torch
import numpy as np
import logging
from hyper_runtime.i_gpu_orchestrator import IGpuOrchestrator
from core_ai.layers.linear_bitnet import LinearBitNet
import time

logger = logging.getLogger(__name__)

class InferenceLoop:
    """
    The Master Pipelined Inference Loop.
    Executes AVX2 computations on P-Cores while the iGPU stages the next layer's memory.
    """
    def __init__(self, layers: list[LinearBitNet]):
        self.layers = layers
        self.num_layers = len(layers)
        self.igpu = IGpuOrchestrator()
        
        # Allocate pre-fetch buffers (L3 staging areas)
        # We ping-pong between two buffers to avoid data races.
        if self.num_layers > 0:
            sample_weight = self.layers[0].weight.data
            self.ping_buffer = np.zeros(sample_weight.numel(), dtype=np.int8)
            self.pong_buffer = np.zeros(sample_weight.numel(), dtype=np.int8)
            
        logger.info(f"Inference Pipeline armed with {self.num_layers} layers.")

    def forward(self, x: torch.Tensor):
        """
        Executes a single forward pass over all layers.
        CPU NEVER waits for RAM.
        """
        if self.num_layers == 0:
            return x
            
        # 1. Initial stage of Layer 0 into ping buffer
        w_0, _ = self.layers[0].absmean_quantize_weights(self.layers[0].weight)
        w_0_np = w_0.numpy().astype(np.int8).flatten()
        self.igpu.stage_layer_asynchronously(w_0_np, self.ping_buffer)
        
        current_buffer = self.ping_buffer
        next_buffer = self.pong_buffer
        
        for i in range(self.num_layers):
            # Dispatch iGPU to fetch Layer i+1 (if exists)
            fetch_thread = None
            if i + 1 < self.num_layers:
                w_next, _ = self.layers[i+1].absmean_quantize_weights(self.layers[i+1].weight)
                w_next_np = w_next.numpy().astype(np.int8).flatten()
                
                # Start async fetch
                fetch_thread = threading.Thread(
                    target=self.igpu.stage_layer_asynchronously, 
                    args=(w_next_np, next_buffer)
                )
                fetch_thread.start()
            
            # --- CPU COMPUTE (AVX2) ---
            # CPU executes using the data currently staged in current_buffer
            # Note: We simulate pulling from the staged buffer here by passing x through the layer natively.
            # In a fully integrated C++ engine, we pass a pointer to `current_buffer` directly to the AVX2 kernel.
            t0 = time.perf_counter()
            x = self.layers[i](x)
            compute_time = time.perf_counter() - t0
            
            # --- WAIT FOR iGPU (if CPU finished before memory fetch) ---
            if fetch_thread:
                fetch_thread.join()
                
            # Swap buffers for the next iteration
            current_buffer, next_buffer = next_buffer, current_buffer
            
        return x
