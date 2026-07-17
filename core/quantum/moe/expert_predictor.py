"""
LEO Expert Predictor
Analyzes input patterns to proactively identify required model experts.
"""
import torch
import time
from typing import List
from collections import defaultdict, deque
import numpy as np

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
        if task_type in self.task_patterns and len(self.task_patterns[task_type]) > 0:
            recent_experts = self.task_patterns[task_type][-10:]
            predicted = list(set(recent_experts))[:num_predict]
        else:
            sorted_experts = sorted(
                self.expert_popularity.items(),
                key=lambda x: x[1],
                reverse=True
            )
            predicted = [exp[0] for exp in sorted_experts[:num_predict]]
        
        if len(predicted) < num_predict:
            remaining = [i for i in range(self.num_experts) if i not in predicted]
            if remaining:
                chosen = np.random.choice(remaining, min(len(remaining), num_predict - len(predicted)), replace=False)
                predicted.extend([int(x) for x in chosen])
        
        if not predicted:
            predicted = list(range(min(num_predict, self.num_experts)))
            
        return predicted[:num_predict]
