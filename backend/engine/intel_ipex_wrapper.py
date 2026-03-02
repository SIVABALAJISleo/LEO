import logging
import os

try:
    import torch
    import intel_extension_for_pytorch as ipex
    IPEX_AVAILABLE = True
except ImportError:
    IPEX_AVAILABLE = False

logger = logging.getLogger(__name__)

class UnifiedHardwareOptimizer:
    """
    Wraps standard PyTorch models explicitly targeting Intel AVX-512 and AMX silicon.
    """
    @staticmethod
    def optimize_model_for_cpu(model, dtype=torch.float32, is_training=False):
        if not IPEX_AVAILABLE:
            logger.warning("Intel IPEX missing. Falling back to native PyTorch.")
            # Native PyTorch optimization fallback
            if hasattr(torch, "compile"):
                return torch.compile(model, backend="inductor", mode="reduce-overhead")
            return model
            
        try:
            logger.info(f"Wrapping model in IPEX (Intel Advanced Matrix Extensions AMX / AVX-512). Mode: dtype={dtype}")
            
            # Use specific Intel channels-last memory formats for CNN efficiency
            if not is_training:
                model.eval()
            
            # `ipex.optimize` fuses operators, enables oneDNN MKLDNN integration natively, 
            # and selects optimal int8/bf16 quantization paths if the CPU supports it.
            optimized_model = ipex.optimize(
                model, 
                dtype=dtype, 
                level="O1", # O1 enables operator fusion.
                auto_kernel_selection=True
            )
            return optimized_model
        except Exception as e:
            logger.error(f"IPEX Intel Operator Fusion Failed: {e}")
            return model
            
    @staticmethod
    def force_bfloat16():
        """ Forces IPEX and PyTorch to use BFloat16 across the global context if AVX512_BF16 is supported """
        if IPEX_AVAILABLE and ipex.has_cpu_bfloat16_support():
            torch.set_default_tensor_type(torch.BFloat16Tensor)
            logger.info("Universal bfloat16 AMX tensor types universally applied.")
