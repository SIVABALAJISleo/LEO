import os
import logging
from typing import List, Optional
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

from archive_engines.closed_loop_synthesis.config import settings

logger = logging.getLogger(__name__)

class Proposer:
    """
    LLM Proposer Layer.
    Generates candidate code based on task and previous failure signals.
    """
    def __init__(self, model_path: str = settings.PROPOSER_MODEL_PATH):
        self.model_path = model_path
        self.llm = None
        if Llama and os.path.exists(self.model_path):
            try:
                self.llm = Llama(
                    model_path=self.model_path,
                    n_ctx=4096,
                    n_threads=os.cpu_count() or 4,
                    verbose=False
                )
            except Exception as e:
                logger.error(f"Failed to load LLM: {e}")

    async def propose(self, task: str, constraints: str, error_summary: Optional[str] = None) -> List[str]:
        """
        Generate k candidates.
        """
        prompt = self._build_prompt(task, constraints, error_summary)
        
        candidates = []
        if self.llm:
            for _ in range(settings.CANDIDATES_PER_ITER):
                output = self.llm(
                    prompt,
                    max_tokens=512,
                    temperature=0.7, # Higher temp for diverse candidates
                    stop=["```", "Task:"],
                    echo=False
                )
                code = self._extract_code(output['choices'][0]['text'])
                if code:
                    candidates.append(code)
        else:
            # Mocking candidates if LLM is not available
            candidates = [self._mock_code(task) for _ in range(settings.CANDIDATES_PER_ITER)]
            
        return candidates

    def _build_prompt(self, task: str, constraints: str, error_summary: Optional[str]) -> str:
        error_context = f"\nPREVIOUS ERROR SIGNAL:\n{error_summary}\nPlease fix this error in your next proposal." if error_summary else ""
        
        return f"""Task: {task}
Constraints: {constraints}
{error_context}

Instruction: Output ONLY the Python code. No explanation. Use type hints.
Code:
```python
"""

    def _extract_code(self, text: str) -> str:
        # Clean up the output to get only the code
        code = text.split("```")[0].strip()
        if code.startswith("python"):
            code = code[6:].strip()
        return code

    def _mock_code(self, task: str) -> str:
        # Simple mock code for demonstration
        if "sum" in task.lower():
            return "def solution(a: int, b: int) -> int:\n    return a + b"
        return "def solution():\n    return 'verified'"
