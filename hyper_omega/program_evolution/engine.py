"""
Program Evolution Engine: Evolves executable AST program populations with
compile, execute, verify, and measure gates before admitting any candidate.
"""
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper_universal.contract_ir import ContractIR, ContractType
from hyper_universal.sandbox.executor import execute_isolated_candidate
from hyper_universal.work_meter import WorkMeter
from hyper_omega.program_evolution.genome import (
    ProgramGenome,
    ProgramMutator,
    ProgramCrossover,
)


class ProgramEvolutionEngine:
    """
    Autonomous evolutionary algorithm mutating and crossing over executable programs.
    Strictly gates every candidate through compile -> execute -> verify -> measure.
    """

    def __init__(self, population_size: int = 10, work_meter: Optional[WorkMeter] = None):
        self.population_size = population_size
        self.work_meter = work_meter or WorkMeter()
        self.population: List[ProgramGenome] = []
        self.generation_count = 0

    def seed_population(self, seed_code: str, initial_genes: Optional[Dict[str, Any]] = None) -> ProgramGenome:
        seed = ProgramGenome(
            genome_id="seed_0",
            generation=0,
            ast_source=seed_code,
            genes=initial_genes or {"unroll_factor": 1, "branchless": False, "precision": "FP32"},
            fitness=1.0,
            measured_speedup=1.0,
            verified=True,
        )
        self.population = [seed]
        return seed

    def evolve_generation(
        self,
        test_inputs: List[Any],
        reference_fn: Callable[[Any], Any],
        contract: ContractIR,
    ) -> List[ProgramGenome]:
        """
        Executes one evolutionary generation:
        1. Select parents
        2. Mutate / Crossover
        3. Compile, Execute in sandbox, Verify contract, Measure real time
        4. Populate survivors
        """
        if not self.population:
            raise ValueError("Population is empty. Call seed_population first.")

        self.generation_count += 1
        new_candidates: List[ProgramGenome] = []

        # Generate candidates via mutation
        for parent in self.population:
            child = ProgramMutator.apply_random_mutation(parent)
            new_candidates.append(child)

        # Generate candidates via crossover if >= 2 parents
        if len(self.population) >= 2:
            p1, p2 = np.random.choice(self.population, 2, replace=False)
            cross_child = ProgramCrossover.crossover(p1, p2)
            new_candidates.append(cross_child)

        # Strictly evaluate every candidate
        verified_offspring: List[ProgramGenome] = []
        for cand in new_candidates:
            verified, speedup = self._evaluate_candidate(cand, test_inputs, reference_fn, contract)
            if verified:
                cand.verified = True
                cand.measured_speedup = speedup
                cand.fitness = speedup  # Fitness proportional to empirical speedup
                verified_offspring.append(cand)

        # Update population keeping top-K by fitness
        combined = self.population + verified_offspring
        # Sort descending by fitness
        combined.sort(key=lambda g: g.fitness, reverse=True)
        self.population = combined[:self.population_size]
        return self.population

    def _evaluate_candidate(
        self,
        candidate: ProgramGenome,
        test_inputs: List[Any],
        reference_fn: Callable[[Any], Any],
        contract: ContractIR,
    ) -> Tuple[bool, float]:
        """Strict compile, sandbox execution, contract check, and empirical measurement."""
        ref_times = []
        cand_times = []

        for inp in test_inputs:
            # 1. Measure reference execution
            t0 = time.perf_counter()
            ref_out = reference_fn(inp)
            t_ref = time.perf_counter() - t0
            ref_times.append(t_ref)

            # 2. Compile and execute isolated candidate
            t1 = time.perf_counter()
            res = execute_isolated_candidate(candidate.ast_source, inp, timeout_seconds=3.0)
            t_cand = time.perf_counter() - t1
            cand_times.append(t_cand)

            if not res.success:
                return False, 0.0

            # 3. Contract verification
            cand_out = res.output
            if contract.contract_type == ContractType.EXACT:
                if isinstance(ref_out, np.ndarray) and isinstance(cand_out, np.ndarray):
                    if not np.array_equal(ref_out, cand_out):
                        return False, 0.0
                elif ref_out != cand_out:
                    return False, 0.0
            elif contract.contract_type == ContractType.NUMERICAL_TOLERANCE:
                max_diff = np.max(np.abs(np.array(ref_out) - np.array(cand_out)))
                if max_diff > contract.absolute_tolerance:
                    return False, 0.0

        avg_ref = float(np.mean(ref_times)) if ref_times else 1e-6
        avg_cand = float(np.mean(cand_times)) if cand_times else 1e-6
        speedup = avg_ref / max(avg_cand, 1e-9)
        return True, speedup
