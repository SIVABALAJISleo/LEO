import random
import re
import subprocess
import os
from typing import List

class MutationEngine:
    """
    7. MUTATION TESTING
    - break code intentionally
    - mutation score >= 90%
    """
    def __init__(self):
        # Common mutations
        self.mutations = [
            (r"\+", "-"),
            (r"-", "+"),
            (r"\*", "/"),
            (r"==", "!="),
            (r">", "<="),
            (r"<", ">="),
            (r"True", "False"),
            (r"False", "True")
        ]

    async def check_mutation_score(self, code: str, test_file_path: str, cwd: str) -> float:
        """
        Calculates mutation score: (Killed Mutants / Total Mutants)
        """
        mutants = self._generate_mutants(code)
        if not mutants: return 1.0 # Nothing to mutate, perfect by default
        
        killed = 0
        total = len(mutants)
        
        for i, mutant_code in enumerate(mutants):
            # Write mutant to temporary solution file
            mutant_path = os.path.join(cwd, "solution.py")
            with open(mutant_path, "w") as f: f.write(mutant_code)
            
            # Run tests
            res = subprocess.run(
                [sys.executable, "-m", "pytest", test_file_path],
                capture_output=True, text=True, timeout=5, cwd=cwd
            )
            
            if res.returncode != 0:
                killed += 1 # Mutant was caught by tests!
        
        return killed / total

    def _generate_mutants(self, code: str) -> List[str]:
        mutants = []
        # Basic line-by-line mutation
        lines = code.split('\n')
        for i, line in enumerate(lines):
            for pattern, replacement in self.mutations:
                if re.search(pattern, line):
                    new_line = re.sub(pattern, replacement, line, count=1)
                    new_mutant = lines.copy()
                    new_mutant[i] = new_line
                    mutants.append('\n'.join(new_mutant))
                    
        # Limit mutants for performance
        if len(mutants) > 10:
            return random.sample(mutants, 10)
        return mutants

import sys
