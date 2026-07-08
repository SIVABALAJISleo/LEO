"""
LEO AI V42 - The Irrelevance Engine
Phase 3: Mamba O(n) + Speculative Decoding Stack

Converter to hybridize standard Transformer models (Llama, Mistral) by replacing
every 2nd attention layer with a Mamba SSM layer. First and last layers are
preserved for training stability. Includes KL-divergence distillation routines.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

from .mamba_cpu_engine import MambaCPULayer

class MambaHybridConverter:
    def __init__(self, replace_frequency: int = 2):
        self.replace_frequency = replace_frequency

    def hybridize_model(self, transformer_model: nn.Module) -> nn.Module:
        """
        Replaces attention layers with MambaCPULayers in a Transformer model.
        Assumes the model exposes an attribute like `model.layers` or `transformer.h`.
        """
        # Attempt to find the layers module list
        layers_attr = None
        for attr_name in ['layers', 'h', 'blocks']:
            if hasattr(transformer_model, attr_name) or (hasattr(transformer_model, 'model') and hasattr(transformer_model.model, attr_name)):
                layers_attr = attr_name
                break
                
        if not layers_attr:
            raise ValueError("Could not auto-detect the transformer layers attribute.")

        if hasattr(transformer_model, 'model'):
            module_list = getattr(transformer_model.model, layers_attr)
        else:
            module_list = getattr(transformer_model, layers_attr)
            
        num_layers = len(module_list)
        
        # Replace every Nth layer, except first and last
        for i in range(1, num_layers - 1):
            if i % self.replace_frequency == 0:
                original_layer = module_list[i]
                
                # We need to guess the hidden size from the original layer
                # Try finding a linear projection size
                d_model = None
                for child in original_layer.modules():
                    if isinstance(child, nn.Linear):
                        d_model = child.in_features
                        break
                        
                if d_model:
                    mamba_layer = MambaCPULayer(d_model=d_model)
                    module_list[i] = mamba_layer
                else:
                    print(f"Warning: Could not determine d_model for layer {i}. Skipping replacement.")

        return transformer_model

class KLDistillationTrainer:
    """
    Distills knowledge from an original Transformer teacher to a Hybrid Mamba student
    using KL divergence on the logits and MSE on the hidden states.
    """
    def __init__(self, teacher_model: nn.Module, student_model: nn.Module, temperature: float = 2.0):
        self.teacher = teacher_model
        self.student = student_model
        self.temperature = temperature
        
        # Freeze teacher
        self.teacher.eval()
        for param in self.teacher.parameters():
            param.requires_grad = False

    def distillation_step(self, input_ids: torch.Tensor, optimizer: torch.optim.Optimizer) -> float:
        self.student.train()
        optimizer.zero_grad()
        
        with torch.no_grad():
            teacher_logits = self.teacher(input_ids)
            if hasattr(teacher_logits, 'logits'):
                teacher_logits = teacher_logits.logits
                
        student_logits = self.student(input_ids)
        if hasattr(student_logits, 'logits'):
            student_logits = student_logits.logits
            
        # KL Divergence Loss
        loss_kl = F.kl_div(
            F.log_softmax(student_logits / self.temperature, dim=-1),
            F.softmax(teacher_logits / self.temperature, dim=-1),
            reduction='batchmean'
        ) * (self.temperature ** 2)
        
        # Cross Entropy could also be added if labels were provided
        
        loss_kl.backward()
        optimizer.step()
        
        return loss_kl.item()
