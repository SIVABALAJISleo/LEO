import asyncio
import logging
from typing import Optional
from archive_engines.closed_loop_synthesis.config import settings
from archive_engines.closed_loop_synthesis.core.proposer import Proposer
from archive_engines.closed_loop_synthesis.core.verifier import Verifier
from archive_engines.closed_loop_synthesis.core.analyzer import ErrorAnalyzer
from archive_engines.closed_loop_synthesis.core.cache import SynthesisCache

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SynthesisEngine")

class SynthesisEngine:
    def __init__(self):
        self.proposer = Proposer()
        self.verifier = Verifier()
        self.analyzer = ErrorAnalyzer()
        self.cache = SynthesisCache()

    async def synthesize(self, task: str, constraints: str = "", tests: str = "") -> Optional[str]:
        """
        100% Correctness Loop.
        """
        logger.info(f"Starting synthesis for task: {task[:50]}...")

        # 7. CACHE (ZERO COMPUTE)
        cached_solution = self.cache.lookup(task)
        if cached_solution:
            logger.info("ZERO-COMPUTE: Semantic cache hit.")
            return cached_solution

        error_summary = None
        
        # 6. ITERATION LOOP
        for iteration in range(settings.MAX_ITERATIONS):
            logger.info(f"Iteration {iteration + 1}/{settings.MAX_ITERATIONS}")
            
            # 2. PROPOSER (LLM)
            candidates = await self.proposer.propose(task, constraints, error_summary)
            
            iteration_errors = []
            
            for i, candidate in enumerate(candidates):
                logger.info(f"Verifying candidate {i+1}/{len(candidates)}...")
                
                # 4. VERIFIER (STRICT)
                result = await self.verifier.verify(candidate, tests)
                
                if result.success:
                    logger.info("VERIFIED: Candidate passed all checks.")
                    # 7. STORE IN CACHE
                    self.cache.store(task, candidate)
                    return candidate
                
                iteration_errors.append(result.stderr or result.stdout)
            
            # 5. ERROR ANALYZER
            error_summary = self.analyzer.summarize_failures(iteration_errors)
            logger.warning(f"All candidates failed in iteration {iteration + 1}. Error Signal: {error_summary}")

        logger.error("Synthesis failed: Maximum iterations reached without verification.")
        return None

async def main():
    engine = SynthesisEngine()
    
    task = "Write a function 'sum_list' that takes a list of integers and returns their sum."
    constraints = "Must use type hints. Must handle empty lists."
    tests = """
def test_sum():
    assert sum_list([1, 2, 3]) == 6
    assert sum_list([]) == 0
    assert sum_list([-1, 1]) == 0
"""
    
    verified_code = await engine.synthesize(task, constraints, tests)
    
    if verified_code:
        print("\n--- VERIFIED CODE ---")
        print(verified_code)
        print("---------------------\n")
    else:
        print("\n--- SYNTHESIS FAILED ---")

if __name__ == "__main__":
    asyncio.run(main())
