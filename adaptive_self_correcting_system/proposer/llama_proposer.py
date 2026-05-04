import os
from typing import List
from ..models.schemas import Solution, SystemSpec

class ProposerBase:
    async def propose(self, spec: SystemSpec, k: int = 5) -> List[Solution]:
        raise NotImplementedError

class LlamaProposer(ProposerBase):
    """
    2. OPEN SYSTEM (PROPOSER)
    - Generate k=5 diverse candidate solutions
    - Optimized for quantized small models (<=7B)
    """
    def __init__(self, model_path: str = "models/stable-code-3b.Q4_K_M.gguf"):
        self.model_path = model_path
        self.llm = None
        self._initialize()

    def _initialize(self):
        try:
            from llama_cpp import Llama
            if os.path.exists(self.model_path):
                self.llm = Llama(model_path=self.model_path, n_ctx=2048, n_threads=4)
            else:
                print(f"Warning: Model not found at {self.model_path}. Using Mock mode.")
        except ImportError:
            print("Warning: llama-cpp-python not installed. Using Mock mode.")

    async def propose(self, spec: SystemSpec, k: int = 5) -> List[Solution]:
        if not self.llm:
            return self._mock_propose(spec, k)
        
        solutions = []
        prompt = self._build_prompt(spec)
        
        for i in range(k):
            # Divergent sampling for diversity
            output = self.llm(
                prompt,
                max_tokens=512,
                temperature=0.8 + (i * 0.05),
                stop=["```\n"]
            )
            code = output["choices"][0]["text"]
            solutions.append(Solution(
                code=code,
                explanation=f"Candidate {i+1}",
                iteration=0,
                proposer_id="llama_cpp"
            ))
        
        return solutions

    def _build_prompt(self, spec: SystemSpec) -> str:
        return f"""
        Write a Python function for the following intent: {spec.intent}
        Constraints: {", ".join(spec.constraints)}
        Invariants: {", ".join(spec.invariants)}
        Return only the code block.
        ```python
        """

    def _mock_propose(self, spec: SystemSpec, k: int = 5) -> List[Solution]:
        # Return a simple mock solution for development
        return [
            Solution(
                code="def solve(input_data):\n    return input_data",
                explanation="Mock candidate",
                iteration=0,
                proposer_id="mock"
            ) for _ in range(k)
        ]
