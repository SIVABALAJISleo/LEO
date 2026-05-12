from llama_cpp import Llama
import os

class CPULLMEngine:
    """
    Layer 6: CPU LLM Engine
    llama.cpp GGUF optimized for CPU.
    """
    def __init__(self, model_path: str = "models/phi-3-mini-4k-instruct.Q4_K_M.gguf"):
        self.model_path = model_path
        self.llm = None
        if os.path.exists(model_path):
            self.llm = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_threads=os.cpu_count() or 4,
                n_batch=512,
                verbose=False
            )

    def generate(self, prompt: str, context: str = "") -> str:
        if not self.llm:
            return f"[MOCK CPU RESPONSE] No model at {self.model_path}"
        
        full_prompt = f"Context: {context}\nUser: {prompt}\nAssistant:"
        output = self.llm(full_prompt, max_tokens=256, stop=["User:"], echo=False)
        return output["choices"][0]["text"].strip()

if __name__ == "__main__":
    engine = CPULLMEngine()
    print(engine.generate("Explain Project HYPER", context="HYPER is zero-gpu."))
