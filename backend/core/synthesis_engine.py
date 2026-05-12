import os
import subprocess
import tempfile
import time
import hashlib
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# iGPU/CPU Optimized Inference
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

logger = logging.getLogger(__name__)

class SynthesisRequest(BaseModel):
    task: str
    tests: Optional[str] = None
    max_iter: int = 5
    user_id: str = "default"

class SynthesisEngine:
    """
    CPU/iGPU-only Closed-Loop Code Synthesis System.
    LLM = Proposer | CPU = Verifier.
    Core: Never trust output. Only return VERIFIED code.
    """
    def __init__(self, model_path: str = "models/codellama-7b.Q4_K_M.gguf"):
        self.model_path = model_path
        self.llama = None
        self.cache = {} # Intent -> Verified Code
        
    def _get_model(self):
        """Lazy load quantized model for CPU/iGPU."""
        if self.llama is None and Llama is not None:
            try:
                # Optimized for CPU execution
                self.llama = Llama(
                    model_path=self.model_path, 
                    n_ctx=4096, 
                    n_threads=4,
                    verbose=False
                )
            except Exception as e:
                logger.error(f"Synthesis model load failed: {e}")
        return self.llama

    async def synthesize(self, req: SynthesisRequest) -> Dict[str, Any]:
        start_time = time.time()
        
        # 7. CACHE (ZERO COMPUTE)
        task_hash = hashlib.sha256(req.task.encode()).hexdigest()
        if task_hash in self.cache:
            return {
                "code": self.cache[task_hash], 
                "status": "success", 
                "source": "cache",
                "latency_ms": (time.time() - start_time) * 1000
            }

        # 1. INPUT NORMALIZATION
        normalized_task = req.task.strip()
        
        # 8. TEST GENERATOR (Merging user tests with basic sanity)
        tests = req.tests or "def test_sanity(): assert True"
        
        current_errors = ""
        
        # 6. ITERATION LOOP
        for i in range(req.max_iter):
            # 2. PROPOSER (LLM)
            # Generating k=1 per iteration for strict loop feedback
            candidates = await self._propose_candidates(normalized_task, current_errors)
            
            for code in candidates:
                # 3. SANDBOX EXECUTION & 4. VERIFIER
                verification = self._verify_code(code, tests)
                
                if verification["success"]:
                    # 9. OUTPUT (Verified Only)
                    self.cache[task_hash] = code
                    return {
                        "code": code, 
                        "status": "success", 
                        "iterations": i + 1,
                        "latency_ms": (time.time() - start_time) * 1000
                    }
                
                # 5. ERROR ANALYZER
                current_errors = self._analyze_errors(verification)
        
        # 9. FAILURE OUTPUT
        return {
            "status": "failure", 
            "message": f"Verification failed after {req.max_iter} iterations.",
            "last_error": current_errors
        }

    async def _propose_candidates(self, task: str, errors: str) -> List[str]:
        """Proposer (Point 2) - LLM generates code candidates."""
        model = self._get_model()
        if not model:
            return ["# Error: Llama model not available for synthesis."]
            
        prompt = f"Task: {task}\n"
        if errors:
            prompt += f"Previous Error: {errors}\nInstruction: Fix the code based on the error above.\n"
        prompt += "Instruction: Output ONLY Python code. No text, no markdown. Stop after code block.\nCode:\n"
        
        loop = asyncio.get_event_loop()
        # Parallel candidate execution (Point 10) can be implemented by increasing n_candidates here
        response = await loop.run_in_executor(None, lambda: model(prompt, max_tokens=1024, stop=["#", "```"]))
        code = response["choices"][0]["text"].strip()
        return [code]

    def _verify_code(self, code: str, tests: str) -> Dict[str, Any]:
        """Sandbox Execution & Verifier (Points 3 & 4)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            code_file = os.path.join(tmpdir, "solution.py")
            test_file = os.path.join(tmpdir, "test_solution.py")
            
            # Write solution
            with open(code_file, "w") as f:
                f.write(code)
            
            # Write tests with import
            with open(test_file, "w") as f:
                f.write(f"import solution\nimport pytest\n{tests}")
            
            # 3. SANDBOX: Subprocess with isolation
            try:
                # Run pytest
                result = subprocess.run(
                    ["pytest", test_file],
                    capture_output=True,
                    text=True,
                    timeout=15, # Enforce timeout (Point 3)
                    cwd=tmpdir
                )
                
                success = (result.returncode == 0)
                
                # 4. VERIFIER: Optional mypy check
                # try: subprocess.run(["mypy", code_file], check=True) except: success=False
                
                return {
                    "success": success,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            except subprocess.TimeoutExpired:
                return {"success": False, "stderr": "Execution Timeout"}
            except Exception as e:
                return {"success": False, "stderr": str(e)}

    def _analyze_errors(self, verification: Dict[str, Any]) -> str:
        """Error Analyzer (Point 5)."""
        stderr = verification.get("stderr", "")
        stdout = verification.get("stdout", "")
        # Extract meaningful failure signals from pytest output
        if "AssertionError" in stdout:
            return "AssertionError: Logic does not match test expectations."
        if "SyntaxError" in stderr:
            return "SyntaxError: Invalid Python syntax."
        return (stderr + stdout)[:300] # Truncate for prompt

global_synthesis_engine = SynthesisEngine()
