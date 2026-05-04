from enum import Enum
from typing import Optional, Dict, Any

class ComputePath(Enum):
    TINY = "tiny"        # ONNX / Heuristics (Local CPU)
    QUANTIZED = "quantized" # llama.cpp GGUF (Local CPU/iGPU)
    HARD = "hard"         # Cloud API (Optional, <5% target)

class Router:
    """
    3. SMART ROUTER (MIN COMPUTE FIRST)
    - Always choose lowest-cost path
    - simple -> tiny model (ONNX)
    - medium -> quantized model (GGUF)
    - hard -> heavy model/API (<=5% usage)
    """
    
    def classify_complexity(self, text: str, intent: str) -> ComputePath:
        text_lower = text.lower()
        
        # 1. Simple Path (TINY)
        # Status checks, small greetings, direct metadata queries
        if intent in ["system_config", "hardware_optimize"] and len(text) < 50:
            return ComputePath.TINY
            
        simple_indicators = ["hi", "hello", "status", "version", "ping"]
        if any(word in text_lower for word in simple_indicators):
            return ComputePath.TINY
            
        # 2. Hard Path (HARD)
        # Deep analysis, complex multi-step reasoning, or huge context
        hard_indicators = ["analyze deep", "comprehensive audit", "refactor entire", "security scan"]
        if any(word in text_lower for word in hard_indicators) or len(text) > 2000:
            return ComputePath.HARD
            
        # 3. Default Path (QUANTIZED)
        # Standard reasoning, code generation, detailed explanations
        return ComputePath.QUANTIZED

class ZeroComputeLayer:
    """
    4. ZERO-COMPUTE LAYER (PRIMARY WEAPON)
    - Semantic cache (similarity > 0.92 -> reuse)
    - Precomputed templates (intent -> solution -> fill variables)
    - Lazy compute: compute once, then store
    """
    def __init__(self, vector_db_service):
        self.vector_db = vector_db_service
        self.templates = {
            "hardware_optimize": "Optimization profile for {target} applied: [Mode: High-Performance, Cache: Enabled, Compute: Local iGPU].",
            "system_config": "System parameter '{parameter}' set to optimal for CPU-first execution.",
            "get_status": "All systems nominal. Intelligence layer latency: <5ms. Model helper: Standby.",
        }

    async def check_cache(self, text: str) -> Optional[str]:
        # Target: 60-80% no compute
        cached = await self.vector_db.search_cache(text, threshold=0.92)
        if cached:
            return cached.content
        return None

    def try_template(self, intent: str, constraints: Dict[str, Any]) -> Optional[str]:
        template = self.templates.get(intent)
        if template:
            try:
                # Only fill if all required keys are present
                return template.format(**constraints)
            except (KeyError, ValueError):
                return template # Return raw template or None
        return None
