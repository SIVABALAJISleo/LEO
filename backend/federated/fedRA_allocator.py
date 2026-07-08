"""
LEO AI V42 - The Irrelevance Engine
Phase 4: Swarm Distillation Protocol (Federated Training Without GPUs)

FedRA: Randomized LoRA Allocation.
Distributes randomly selected subsets of LoRA adapters to heterogeneous swarm clients
to prevent individual overfitting and balance compute capabilities.
"""

import random
from typing import List, Dict, Any, Optional

class FedRAAllocator:
    def __init__(self, global_lora_registry: List[str]):
        """
        global_lora_registry: List of all target layer names that have LoRA adapters.
        e.g., ["layer_0_attention", "layer_1_mlp", ..., "layer_79_attention"]
        """
        self.global_registry = global_lora_registry
        
    def allocate_adapters(self, client_capabilities: Dict[str, Any]) -> List[str]:
        """
        Determines how many and which LoRA adapters a client should train.
        Heterogeneous device support:
        - Mobile/Browser: 1-2 adapters
        - Standard Laptop: 4-8 adapters
        - High-End CPU: 10-20 adapters
        """
        ram_gb = client_capabilities.get("ram_gb", 8)
        flops_est = client_capabilities.get("flops_est", 1.0)
        
        # Determine capacity budget
        if ram_gb < 4 or flops_est < 0.5:
            budget = 1
        elif ram_gb < 16 or flops_est < 5.0:
            budget = 4
        else:
            budget = 10
            
        # Ensure budget doesn't exceed total available adapters
        budget = min(budget, len(self.global_registry))
        
        # Randomly sample the registry to prevent overfitting to a single client's data
        # FedRA ensures that across the swarm, the network is uniformly updated
        allocated = random.sample(self.global_registry, budget)
        
        return allocated

    def adaptive_fedavg(self, client_deltas: List[Dict[str, Any]], layer_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Performs Federated Averaging (FedAvg) over the received LoRA deltas.
        Adapts learning rates based on client reliability and data novelty.
        """
        aggregated = {}
        counts = {}
        
        for client_idx, delta_payload in enumerate(client_deltas):
            # Evaluate client reputation/weighting
            client_weight = layer_weights[str(client_idx)] if layer_weights else 1.0
            
            for layer_name, tensor_data in delta_payload.items():
                if layer_name not in aggregated:
                    aggregated[layer_name] = tensor_data * client_weight
                    counts[layer_name] = client_weight
                else:
                    aggregated[layer_name] += (tensor_data * client_weight)
                    counts[layer_name] += client_weight
                    
        # Average the accumulated deltas
        for layer_name in aggregated.keys():
            aggregated[layer_name] = aggregated[layer_name] / counts[layer_name]
            
        return aggregated
