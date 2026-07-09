import logging
import numpy as np
import uuid

class SplitLoRATrainer:
    def __init__(self, base_model: str, lora_rank: int = 8):
        self.logger = logging.getLogger("SplitLoRATrainer")
        self.base_model = base_model
        self.lora_rank = lora_rank
        self.logger.info(f"Initialized SplitLoRA for {base_model} with rank {lora_rank}")
        
    def client_forward(self, prompt: str, client_model_state: dict) -> dict:
        """
        Privacy: raw data never leaves client
        Only intermediate activations (the 'split' boundary) are sent to the Swarm.
        """
        self.logger.debug(f"Client executing forward pass for prompt length {len(prompt)}")
        
        # Simulate computing embeddings and first N layers on client device
        seq_len = len(prompt.split())
        hidden_dim = client_model_state.get("hidden_size", 4096)
        
        # Simulated intermediate activation
        intermediate_activations = np.random.randn(1, seq_len, hidden_dim).astype(np.float32)
        
        return {
            "session_id": str(uuid.uuid4()),
            "split_activations": intermediate_activations,
            "seq_len": seq_len
        }
        
    def server_backward(self, activations: dict, labels: list) -> dict:
        """
        Server computes loss and backward pass on the upper layers.
        Updates LoRA adapters only (not full model) to save bandwidth and compute.
        Returns: updated LoRA deltas to client
        """
        session = activations.get("session_id", "unknown")
        seq_len = activations.get("seq_len", 1)
        hidden_dim = activations["split_activations"].shape[-1]
        
        self.logger.debug(f"Server received split activations for session {session}. Computing loss...")
        
        # Simulate backpropagation through server-side layers
        # Loss calculation vs labels (mocked)
        loss = np.random.random() * 2.0
        
        # Simulated LoRA gradients (A and B matrices)
        lora_A_grad = np.random.randn(hidden_dim, self.lora_rank).astype(np.float32) * 0.01
        lora_B_grad = np.random.randn(self.lora_rank, hidden_dim).astype(np.float32) * 0.01
        
        return {
            "session_id": session,
            "loss": loss,
            "lora_A_delta": lora_A_grad,
            "lora_B_delta": lora_B_grad
        }
        
    def aggregate_lora(self, client_deltas: list) -> dict:
        """
        Aggregate LoRA deltas from multiple clients using FedAvg.
        Weighted by data quality and node reputation.
        """
        if not client_deltas:
            return {}
            
        self.logger.info(f"Aggregating {len(client_deltas)} client LoRA deltas via FedAvg.")
        
        # Extract weights (reputation score)
        weights = np.array([delta.get("reputation", 1.0) for delta in client_deltas])
        weights = weights / np.sum(weights) # Normalize
        
        # Compute weighted average of A matrices
        agg_A = np.zeros_like(client_deltas[0]["lora_A_delta"])
        agg_B = np.zeros_like(client_deltas[0]["lora_B_delta"])
        
        for i, delta in enumerate(client_deltas):
            agg_A += delta["lora_A_delta"] * weights[i]
            agg_B += delta["lora_B_delta"] * weights[i]
            
        return {
            "aggregated_A": agg_A,
            "aggregated_B": agg_B,
            "clients_merged": len(client_deltas)
        }
