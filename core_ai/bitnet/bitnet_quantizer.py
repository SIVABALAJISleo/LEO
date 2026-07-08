"""
LEO AI V42 - The Irrelevance Engine
Phase 1: BitNet Native Layer (1.58-bit Ternary Weights)

Quantizer utility to convert HuggingFace models into 1.58-bit packed representations.
Uses block-based absolute mean processing for optimal accuracy recovery.
"""

import math
import os
import torch
import torch.nn as nn
from tqdm import tqdm

from .bitnet_native_engine import BitLinear

def _quantize_weights_block(w: torch.Tensor, block_size: int = 128):
    """
    Quantizes a 2D weight matrix into 1.58-bit ternary using block-wise absmean scaling.
    """
    out_features, in_features = w.shape
    
    # Pad if necessary so in_features is divisible by block_size
    pad_len = (block_size - (in_features % block_size)) % block_size
    if pad_len > 0:
        w = torch.nn.functional.pad(w, (0, pad_len))
        
    num_blocks = w.shape[1] // block_size
    w_blocked = w.view(out_features, num_blocks, block_size)
    
    # Calculate scale per block
    scale = w_blocked.abs().mean(dim=-1, keepdim=True).clamp(min=1e-5)
    
    # Quantize to {-1, 0, 1}
    w_quant = torch.round(w_blocked / scale).clamp(-1, 1).to(torch.int8)
    
    # Flatten back
    w_quant = w_quant.view(out_features, -1)[:, :in_features]
    scale = scale.view(out_features, num_blocks).to(torch.float16)
    
    return w_quant, scale

def pack_ternary_weights(w_quant: torch.Tensor):
    """
    Packs ternary int8 weights into int32.
    Each int32 stores 16 ternary values.
    Encoding: -1 -> 00, 0 -> 01, +1 -> 10
    """
    out_features, in_features = w_quant.shape
    packed_cols = math.ceil(in_features / 16)
    packed = torch.zeros((out_features, packed_cols), dtype=torch.int32)
    
    for i in range(out_features):
        for j in range(in_features):
            block = j // 16
            offset = j % 16
            
            val = w_quant[i, j].item()
            mapped = val + 1 # 0, 1, 2
            
            packed[i, block] |= (mapped << (offset * 2))
            
    return packed

class BitNetQuantizer:
    def __init__(self, block_size: int = 128):
        self.block_size = block_size

    def quantize_model(self, model: nn.Module) -> nn.Module:
        """
        Recursively replaces all nn.Linear layers in the model with BitLinear layers,
        and quantizes their weights to 1.58-bit packed format.
        """
        self._replace_linear_modules(model)
        return model
        
    def _replace_linear_modules(self, module: nn.Module):
        for name, child in module.named_children():
            if isinstance(child, nn.Linear):
                # Only quantize linear layers that have weights (exclude biases if needed, but BitLinear handles bias)
                bit_linear = BitLinear(
                    in_features=child.in_features,
                    out_features=child.out_features,
                    bias=(child.bias is not None)
                )
                
                # Copy bias
                if child.bias is not None:
                    bit_linear.bias.data.copy_(child.bias.data)
                    
                # We do full model block quantization
                # Notice: Standard BitLinear uses per-channel (out_features) quantization, 
                # but we can enhance it with block-based quantization if needed.
                # For compatibility with our BitLinear class which currently expects per-channel, 
                # we'll use the standard pack_weights from the engine.
                
                # However, since the prompt specifies block-based absolute mean processing,
                # let's inject our block-wise quantized weights into the BitLinear layer.
                
                w_quant, scale = _quantize_weights_block(child.weight.data, self.block_size)
                packed_w = pack_ternary_weights(w_quant)
                
                bit_linear.packed_weight.copy_(packed_w)
                
                # Store the block scales (the current BitLinear class might need an update to support 
                # 2D block scales instead of 1D per-channel scales, but for now we store it).
                # We will adapt bit_linear to accept the block scales.
                bit_linear.register_buffer("block_scale", scale)
                bit_linear.is_packed = True
                bit_linear.weight = None
                
                setattr(module, name, bit_linear)
            else:
                self._replace_linear_modules(child)

    def save_quantized(self, model: nn.Module, save_dir: str):
        """Saves the packed BitNet model to disk."""
        os.makedirs(save_dir, exist_ok=True)
        torch.save(model.state_dict(), os.path.join(save_dir, "bitnet_model.pt"))
        print(f"Saved BitNet quantized model to {save_dir}")

def load_quantized(model_class, save_dir: str, **kwargs):
    """Loads a quantized BitNet model."""
    model = model_class(**kwargs)
    # Instantiate the quantizer just to replace the layers (don't perform quantization)
    quantizer = BitNetQuantizer()
    
    def _dummy_replace(module):
        for name, child in module.named_children():
            if isinstance(child, nn.Linear):
                bit_linear = BitLinear(child.in_features, child.out_features, bias=(child.bias is not None))
                bit_linear.is_packed = True
                bit_linear.weight = None
                setattr(module, name, bit_linear)
            else:
                _dummy_replace(child)
                
    _dummy_replace(model)
    model.load_state_dict(torch.load(os.path.join(save_dir, "bitnet_model.pt")))
    return model
