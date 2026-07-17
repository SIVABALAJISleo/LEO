"""
Dynamic Expert Router for Memory-Efficient MoE
Predicts and loads only required experts
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple
import numpy as np
from collections import defaultdict, deque
import time

class ExpertPredictor:
    """
    Predicts which experts will be needed based on routing patterns
    """
    
    def __init__(self, num_experts: int, history_size: int = 1000):
        self.num_experts = num_experts
        self.history_size = history_size
        self.routing_history = deque(maxlen=history_size)
        self.expert_popularity = defaultdict(int)
        self.task_patterns = defaultdict(list)
        
    def record_routing(self, token: torch.Tensor, expert_id: int, task_type: str):
        """Record routing decision for pattern learning"""
        self.routing_history.append({
            'token': token.detach().cpu(),
            'expert_id': expert_id,
            'task_type': task_type,
            'timestamp': time.time()
        })
        self.expert_popularity[expert_id] += 1
        self.task_patterns[task_type].append(expert_id)
    
    def predict_experts(
        self,
        input_tokens: torch.Tensor,
        task_type: str,
        num_predict: int = 2
    ) -> List[int]:
        """Predict which experts will be needed"""
        # Use historical patterns for prediction
        if task_type in self.task_patterns and len(self.task_patterns[task_type]) > 0:
            # Use task-specific patterns
            recent_experts = self.task_patterns[task_type][-10:]
            predicted = list(set(recent_experts))[:num_predict]
        else:
            # Use global popularity
            sorted_experts = sorted(
                self.expert_popularity.items(),
                key=lambda x: x[1],
                reverse=True
            )
            predicted = [exp[0] for exp in sorted_experts[:num_predict]]
        
        # Add some exploration
        if len(predicted) < num_predict:
            remaining = [i for i in range(self.num_experts) if i not in predicted]
            if remaining:
                chosen = np.random.choice(remaining, min(len(remaining), num_predict - len(predicted)), replace=False)
                predicted.extend([int(x) for x in chosen])
        
        # Fallback to defaults if list is still empty
        if not predicted:
            predicted = list(range(min(num_predict, self.num_experts)))
            
        return predicted[:num_predict]


class DynamicExpertRouter(nn.Module):
    """
    Dynamic router that loads experts on-demand
    """
    
    def __init__(
        self,
        num_experts: int,
        expert_dim: int,
        predictor: Optional[ExpertPredictor] = None,
        max_active_experts: int = 4
    ):
        super().__init__()
        self.num_experts = num_experts
        self.expert_dim = expert_dim
        self.max_active_experts = max_active_experts
        
        # Gating network
        self.gate = nn.Linear(expert_dim, num_experts)
        
        # Expert predictor
        self.predictor = predictor or ExpertPredictor(num_experts)
        
        # Active experts cache
        self.active_experts = {}
        self.expert_usage = defaultdict(int)
        
        # Expert storage (would be on disk in practice)
        self.expert_storage = {}
        self._initialize_experts()
    
    def _initialize_experts(self):
        """Initialize all experts in storage"""
        for i in range(self.num_experts):
            # Create expert (would be loaded from disk)
            self.expert_storage[i] = nn.Sequential(
                nn.Linear(self.expert_dim, self.expert_dim * 4),
                nn.ReLU(),
                nn.Linear(self.expert_dim * 4, self.expert_dim)
            )
    
    def forward(
        self,
        x: torch.Tensor,
        task_type: str = 'general'
    ) -> Tuple[torch.Tensor, List[int]]:
        """
        Route input to experts dynamically
        
        Returns:
            output: Combined expert outputs
            active_experts: List of expert IDs that were activated
        """
        batch_size, seq_len, dim = x.shape
        
        # Predict required experts
        predicted_experts = self.predictor.predict_experts(
            x, task_type, num_predict=self.max_active_experts
        )
        
        # Load predicted experts if not active
        for expert_id in predicted_experts:
            if expert_id not in self.active_experts:
                self._load_expert(expert_id)
        
        # Get gating scores
        gate_scores = self.gate(x)  # [batch, seq, num_experts]
        
        # Select top-k experts
        k_val = min(self.max_active_experts, self.num_experts)
        top_k_scores, top_k_indices = torch.topk(
            gate_scores, 
            k=k_val,
            dim=-1
        )
        
        # Normalize scores
        top_k_scores = F.softmax(top_k_scores, dim=-1)
        
        # Compute expert outputs
        outputs = torch.zeros_like(x)
        active_experts = set()
        
        for i in range(top_k_indices.shape[-1]):
            expert_id = top_k_indices[0, 0, i].item()
            if expert_id in self.active_experts:
                expert = self.active_experts[expert_id]
                expert_output = expert(x)
                outputs += top_k_scores[:, :, i:i+1] * expert_output
                active_experts.add(expert_id)
                self.expert_usage[expert_id] += 1
                
                # Record routing for learning
                self.predictor.record_routing(x[0, 0], expert_id, task_type)
        
        # Evict least recently used experts if cache is full
        if len(self.active_experts) > self.max_active_experts:
            self._evict_experts()
        
        return outputs, list(active_experts)
    
    def _load_expert(self, expert_id: int):
        """Load expert from storage to active cache"""
        if len(self.active_experts) >= self.max_active_experts:
            self._evict_experts()
        
        self.active_experts[expert_id] = self.expert_storage[expert_id]
        self.expert_usage[expert_id] = 1
    
    def _evict_experts(self):
        """Evict least recently used experts"""
        while len(self.active_experts) > self.max_active_experts - 1:
            least_used = min(
                self.active_experts.keys(),
                key=lambda x: self.expert_usage[x]
            )
            del self.active_experts[least_used]
            self.expert_usage[least_used] = 0
