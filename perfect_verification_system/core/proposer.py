import os
from typing import List, Optional
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

class Proposer:
    def __init__(self, model_path: str = "models/phi-3-mini-4k-instruct-q4.gguf"):
        self.model_path = model_path
        self.llm = None
        if Llama and os.path.exists(model_path):
            self.llm = Llama(model_path=model_path, n_ctx=4096, n_threads=4, verbose=False)

    async def propose(self, task: str, constraints: str, error_summary: Optional[str] = None, k: int = 5) -> List[str]:
        prompt = f"{task}\nConstraints: {constraints}\nErrors: {error_summary}\nCode:\n```python\n"
        if self.llm:
            results = []
            for _ in range(k):
                res = self.llm(prompt, max_tokens=512, stop=["```"], temperature=0.8)
                results.append(res['choices'][0]['text'].strip())
            return results
        return ["# Mock candidate\ndef solution(): pass"] * k
