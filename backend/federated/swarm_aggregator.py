"""
LEO AI V42 - The Irrelevance Engine
Phase 4: Swarm Distillation Protocol (Federated Training Without GPUs)

Swarm Aggregator: Central or decentralized server that aggregates LoRA deltas
from thousands of clients using PBFT (Practical Byzantine Fault Tolerance) 
to reject outliers and malicious updates, then applies weighted FedAvg.
"""

import time
import torch
from typing import Dict, List, Any
from collections import defaultdict

from .fedRA_allocator import FedRAAllocator

class PBFTValidator:
    """
    Practical Byzantine Fault Tolerance validator for federated updates.
    Rejects malicious or noisy deltas before they poison the global model.
    """
    def __init__(self, tolerance_std: float = 3.0):
        self.tolerance_std = tolerance_std

    def validate_deltas(self, client_deltas: List[Dict[str, torch.Tensor]]) -> List[Dict[str, torch.Tensor]]:
        """
        Computes the distribution of updates per layer.
        Rejects client updates that fall outside the acceptable standard deviation.
        """
        if len(client_deltas) < 3:
            # Not enough peers to establish consensus, accept all tentatively
            return client_deltas
            
        valid_deltas = []
        
        # Simplified PBFT outlier detection: calculate layer norm statistics
        layer_norms = defaultdict(list)
        for i, delta in enumerate(client_deltas):
            for layer_name, tensor in delta.items():
                layer_norms[layer_name].append((i, torch.norm(tensor.float()).item()))
                
        # Determine valid clients per layer
        malicious_clients = set()
        for layer_name, norms in layer_norms.items():
            vals = [n[1] for n in norms]
            mean = sum(vals) / len(vals)
            var = sum((x - mean) ** 2 for x in vals) / len(vals)
            std = var ** 0.5
            
            for client_idx, norm_val in norms:
                if std > 0 and abs(norm_val - mean) > self.tolerance_std * std:
                    malicious_clients.add(client_idx)
                    
        for i, delta in enumerate(client_deltas):
            if i not in malicious_clients:
                valid_deltas.append(delta)
                
        return valid_deltas

class SwarmAggregator:
    def __init__(self, global_registry: List[str]):
        self.fedra = FedRAAllocator(global_registry)
        self.pbft = PBFTValidator(tolerance_std=3.0)
        
        self.global_state = {}
        self.version_history = []
        self.current_version = 0

    def process_incoming_deltas(self, client_payloads: List[Dict[str, Any]]):
        """
        Main pipeline:
        1. Receive raw deltas from Swarm.
        2. PBFT validation (reject Byzantine/outlier nodes).
        3. FedRA Adaptive Aggregation.
        4. Commit to global state.
        """
        # Extract tensors from payloads
        raw_deltas = [payload["deltas"] for payload in client_payloads]
        client_weights = {str(i): payload.get("reputation_score", 1.0) for i, payload in enumerate(client_payloads)}
        
        # PBFT validation
        valid_deltas = self.pbft.validate_deltas(raw_deltas)
        
        if not valid_deltas:
            print("SwarmAggregator: All deltas rejected by PBFT.")
            return False
            
        # Filter weights for valid clients only
        valid_weights = {}
        valid_idx = 0
        for i in range(len(raw_deltas)):
            if raw_deltas[i] in valid_deltas:
                valid_weights[str(valid_idx)] = client_weights[str(i)]
                valid_idx += 1
        
        # FedRA Aggregation
        aggregated_deltas = self.fedra.adaptive_fedavg(valid_deltas, layer_weights=valid_weights)
        
        # Apply to global state
        self._commit_to_global_state(aggregated_deltas)
        return True

    def _commit_to_global_state(self, aggregated_deltas: Dict[str, torch.Tensor]):
        """
        Updates the global LoRA weights and saves a snapshot (git-like versioning).
        """
        for layer_name, tensor in aggregated_deltas.items():
            if layer_name not in self.global_state:
                self.global_state[layer_name] = tensor.clone()
            else:
                self.global_state[layer_name] += tensor # In reality, apply optimizer step here
                
        self.current_version += 1
        self.version_history.append({
            "version": self.current_version,
            "timestamp": time.time(),
            "layers_updated": list(aggregated_deltas.keys())
        })
        
        print(f"SwarmAggregator: Global model updated to version v{self.current_version}")
