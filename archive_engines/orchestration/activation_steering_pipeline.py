import time
import logging
import asyncio
from typing import Dict, Any, List

try:
    import numpy as np
except ImportError:
    pass

logger = logging.getLogger(__name__)

# =====================================================================
# ACTIVATION STEERING HYBRID AI ARCHITECTURE (CPU+iGPU)
# =====================================================================

class PerceptionLayer:
    """LAYER 10: PERCEPTION - Instant ACK & Streaming"""
    async def acknowledge(self, query: str) -> None:
        # Instant <100ms ACK and partial output setup
        print(f"[\033[93mACK\033[0m] Receiving: '{query[:35]}...'")
        await asyncio.sleep(0.01)

class BaseModel:
    """LAYER 1: BASE MODEL - Always active small quantized LLM"""
    def __init__(self):
        self.model_name = "phi-3-mini-4k-instruct.Q4_K_M.gguf"
        self.kv_cache_active = True
        logger.info(f"Loaded Base Model: {self.model_name}")

class SteeringEngine:
    """LAYER 2: CONTROL VECTOR SYSTEM - Activation Steering"""
    def __init__(self):
        # Precomputed Control Vectors (KB size each)
        # Represents domains, tone, behavior directions in latent space
        self.control_vectors = {
            "formal": np.array([0.1, -0.05, 0.2]),
            "creative": np.array([-0.2, 0.3, 0.1]),
            "concise": np.array([0.4, 0.0, -0.1]),
            "detailed": np.array([-0.1, 0.2, 0.5]),
            "coding": np.array([0.0, 0.5, -0.2]),
            "philosophy": np.array([0.2, 0.1, 0.4])
        }
        
    def build_injection_vector(self, weights: Dict[str, float]) -> np.ndarray:
        """Combine vectors: V = Σ (weight_i * vector_i)"""
        if not weights:
            return np.zeros(3)
            
        V = np.zeros(3)
        active_domains = []
        for domain, weight in weights.items():
            if domain in self.control_vectors and weight > 0:
                V += weight * self.control_vectors[domain]
                active_domains.append(f"{domain}({weight:.2f})")
                
        self.last_active = " + ".join(active_domains) if active_domains else "base"
        return V

class SoftRouter:
    """LAYER 3: INTENT PARSER + SOFT ROUTER - Multi-label classification"""
    def extract_intent(self, query: str) -> Dict[str, Any]:
        query_lower = query.lower()
        intent = {
            "weights": {}, 
            "need_tools": False, 
            "need_retrieval": False,
            "is_complex": False
        }
        
        # Multi-label assignment
        if any(op in query_lower for op in ['+', '-', '*', '/', 'calculate', 'equation']):
            intent["need_tools"] = True
            intent["tool_type"] = "calculator"
        if "code" in query_lower or "python" in query_lower or "function" in query_lower:
            intent["weights"]["coding"] = 0.8
            intent["weights"]["formal"] = 0.5
            intent["need_tools"] = True
            intent["tool_type"] = "executor"
        if "poem" in query_lower or "story" in query_lower:
            intent["weights"]["creative"] = 0.9
        if "explain" in query_lower or "what is" in query_lower or "who is" in query_lower:
            intent["need_retrieval"] = True
            intent["weights"]["detailed"] = 0.7
            if "deep" in query_lower or "complex" in query_lower or "implications" in query_lower:
                intent["is_complex"] = True
                intent["weights"]["philosophy"] = 0.6
                
        # Default steering if none detected
        if not intent["weights"] and not intent["need_tools"]:
            intent["weights"]["concise"] = 0.8
            
        return intent

class KnowledgeSystem:
    """LAYER 4: RAG - Mandatory for Facts"""
    def retrieve(self, query: str) -> List[str]:
        # No factual answer without retrieval context
        return ["[DOC-1] Factual data retrieved from FAISS Vector DB."]

class SymbolicToolLayer:
    """LAYER 5: SYMBOLIC TOOL LAYER - Deterministic execution"""
    def execute(self, tool_type: str, query: str) -> str:
        # Route to: math -> calculator, logic -> rule engine, code -> executor
        return f"[TOOL:{tool_type.upper()}] Deterministic result computed. No LLM guessing."

class GenerationPipeline:
    """LAYER 6: GENERATION PIPELINE - Inject vector into hidden layers"""
    def __init__(self, base_model: BaseModel, steering: SteeringEngine):
        self.base_model = base_model
        self.steering = steering
        
    def generate(self, query: str, intent: Dict[str, Any], context: List[str]) -> str:
        # Build V
        self.steering.build_injection_vector(intent["weights"])
        
        ctx_str = " | ".join(context) if context else "No factual context"
        
        # Simulate generating output with Activation Steering injected
        return f"[GENERATOR] [Steering: {self.steering.last_active}] Generated using context: {ctx_str}"

class TestTimeCompute:
    """LAYER 7: TEST-TIME COMPUTE - Limited for complex queries"""
    def __init__(self, generator: GenerationPipeline):
        self.generator = generator
        
    def evaluate(self, query: str, intent: Dict[str, Any], context: List[str]) -> str:
        # Generate N=2-3 outputs
        candidates = [self.generator.generate(query, intent, context) for _ in range(3)]
        # Evaluate via consistency check and retrieval grounding
        return f"[TEST-TIME-COMPUTE] Selected optimal result from N=3 candidates. {candidates[0]}"

class ErrorControl:
    """LAYER 9: ERROR CONTROL - Confidence & Self-Check"""
    def verify(self, response: str, requires_source: bool) -> bool:
        if requires_source and "[DOC" not in response and "TOOL" not in response:
            return False # Fallback or clarify
        return True

class ActivationSteeringPipeline:
    """
    LAYER 8: PERFORMANCE - Master Pipeline orchestrating async execution, 
    in-memory caching, and KV cache reuse on OpenVINO / llama.cpp.
    """
    def __init__(self):
        self.perception = PerceptionLayer()
        self.base_model = BaseModel()
        self.steering = SteeringEngine()
        self.router = SoftRouter()
        self.knowledge = KnowledgeSystem()
        self.tools = SymbolicToolLayer()
        self.generator = GenerationPipeline(self.base_model, self.steering)
        self.ttc = TestTimeCompute(self.generator)
        self.error_control = ErrorControl()
        
        # Semantic Caching
        self.cache: Dict[str, str] = {}

    async def process_query(self, query: str) -> str:
        start_time = time.perf_counter()
        
        # 1. Perception
        await self.perception.acknowledge(query)
        
        # 2. Semantic Cache
        if query in self.cache:
            latency = (time.perf_counter() - start_time) * 1000
            return f"{self.cache[query]} [CACHED {latency:.2f}ms]"
            
        # 3. Intent & Routing
        intent = self.router.extract_intent(query)
        
        # 4. Deterministic Tools Fast-Path
        if intent["need_tools"] and not intent["need_retrieval"]:
            final_response = self.tools.execute(intent["tool_type"], query)
        else:
            # 5. Mandatory RAG
            context = []
            if intent["need_retrieval"]:
                context = self.knowledge.retrieve(query)
                
            # 6 & 7. Generation or Test-Time Compute
            if intent["is_complex"]:
                raw_response = self.ttc.evaluate(query, intent, context)
            else:
                raw_response = self.generator.generate(query, intent, context)
                
            # 9. Error Control
            is_valid = self.error_control.verify(raw_response, requires_source=intent["need_retrieval"])
            if not is_valid:
                final_response = "I cannot verify the source. Could you clarify your question?"
            else:
                final_response = raw_response
                
        # Cache Result
        self.cache[query] = final_response
            
        latency = (time.perf_counter() - start_time) * 1000
        return f"{final_response} [LATENCY {latency:.2f}ms]"

# =====================================================================
# EXECUTION ENTRY POINT
# =====================================================================
async def main():
    pipeline = ActivationSteeringPipeline()
    print("Initializing Activation Steering Hybrid AI (CPU+iGPU)...\n")
    
    test_queries = [
        "Calculate the mathematical derivative of x^2.",
        "Write a python function to compute the Fibonacci sequence.",
        "Explain the complex implications of quantum entanglement.",
        "Write a short creative poem about a robot.",
        "Explain the complex implications of quantum entanglement." # Should hit cache
    ]
    
    for q in test_queries:
        print(f"\nUser: {q}")
        response = await pipeline.process_query(q)
        print(f"System: {response}")
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())
