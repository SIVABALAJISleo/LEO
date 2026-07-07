import os
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

class HybridModelManager:
    """
    Manages local quantized models for the Open/Closed systems.
    """
    def __init__(self, model_path: str = "models/phi-3-mini-4k-instruct-q4.gguf"):
        self.model_path = model_path
        self.llm = None
        if Llama and os.path.exists(model_path):
            self.llm = Llama(model_path=model_path, n_ctx=4096, n_threads=4, verbose=False)

    def generate(self, prompt: str, k: int = 3) -> List[str]:
        if not self.llm:
            return ["# LLM not loaded. Returning mock proposal.\ndef solution(): return True"] * k
            
        results = []
        for _ in range(k):
            res = self.llm(prompt, max_tokens=512, stop=["```"], temperature=0.7)
            results.append(res['choices'][0]['text'].strip())
        return results
