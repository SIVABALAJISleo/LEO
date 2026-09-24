"""
Program Genome and Genetic Operators:
Models executable programs as genomes with AST transformations, mutation, and crossover.
"""
from dataclasses import dataclass, field
import hashlib
import random
import copy
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ProgramGenome:
    genome_id: str
    generation: int
    ast_source: str
    genes: Dict[str, Any] = field(default_factory=dict)
    fitness: float = 0.0
    measured_speedup: float = 1.0
    verified: bool = False
    mutations_applied: List[str] = field(default_factory=list)
    parent_ids: List[str] = field(default_factory=list)

    @property
    def hash(self) -> str:
        return hashlib.sha256(self.ast_source.encode()).hexdigest()[:16]


class ProgramMutator:
    """Applies genetic mutations to program source and architectural parameters."""

    @staticmethod
    def mutate_loop(genome: ProgramGenome) -> ProgramGenome:
        child = copy.deepcopy(genome)
        child.generation += 1
        child.parent_ids = [genome.genome_id]
        child.genome_id = f"gen_{child.generation}_{random.randint(1000, 9999)}"

        current_unroll = child.genes.get("unroll_factor", 1)
        new_unroll = 4 if current_unroll == 1 else (8 if current_unroll == 4 else 1)
        child.genes["unroll_factor"] = new_unroll
        child.mutations_applied.append(f"loop_unroll_{new_unroll}x")

        # Update AST source with unrolling comment / pragmas
        child.ast_source = (
            f"# [GENOME MUTATION: loop_unroll={new_unroll}x]\n"
            + child.ast_source.replace("# [GENOME MUTATION", "# [PREV")
        )
        return child

    @staticmethod
    def mutate_branch(genome: ProgramGenome) -> ProgramGenome:
        child = copy.deepcopy(genome)
        child.generation += 1
        child.parent_ids = [genome.genome_id]
        child.genome_id = f"gen_{child.generation}_{random.randint(1000, 9999)}"

        branchless = not child.genes.get("branchless", False)
        child.genes["branchless"] = branchless
        child.mutations_applied.append("branchless_masking" if branchless else "branch_restored")
        child.ast_source = (
            f"# [GENOME MUTATION: branchless={branchless}]\n"
            + child.ast_source
        )
        return child

    @staticmethod
    def mutate_precision(genome: ProgramGenome) -> ProgramGenome:
        child = copy.deepcopy(genome)
        child.generation += 1
        child.parent_ids = [genome.genome_id]
        child.genome_id = f"gen_{child.generation}_{random.randint(1000, 9999)}"

        precisions = ["FP32", "FP16", "INT8"]
        curr = child.genes.get("precision", "FP32")
        next_prec = precisions[(precisions.index(curr) + 1) % len(precisions)]
        child.genes["precision"] = next_prec
        child.mutations_applied.append(f"precision_{next_prec}")
        child.ast_source = (
            f"# [GENOME MUTATION: precision={next_prec}]\n"
            + child.ast_source
        )
        return child

    @staticmethod
    def mutate_kernel_fusion(genome: ProgramGenome) -> ProgramGenome:
        child = copy.deepcopy(genome)
        child.generation += 1
        child.parent_ids = [genome.genome_id]
        child.genome_id = f"gen_{child.generation}_{random.randint(1000, 9999)}"

        fused = not child.genes.get("kernel_fused", False)
        child.genes["kernel_fused"] = fused
        child.mutations_applied.append("kernel_fusion" if fused else "kernel_split")
        child.ast_source = (
            f"# [GENOME MUTATION: fused={fused}]\n"
            + child.ast_source
        )
        return child

    @classmethod
    def apply_random_mutation(cls, genome: ProgramGenome) -> ProgramGenome:
        mutators = [
            cls.mutate_loop,
            cls.mutate_branch,
            cls.mutate_precision,
            cls.mutate_kernel_fusion,
        ]
        chosen = random.choice(mutators)
        return chosen(genome)


class ProgramCrossover:
    """Performs semantic crossover between two parent genomes."""

    @staticmethod
    def crossover(parent_a: ProgramGenome, parent_b: ProgramGenome) -> ProgramGenome:
        gen = max(parent_a.generation, parent_b.generation) + 1
        child_id = f"cross_{gen}_{random.randint(1000, 9999)}"

        child_genes = copy.deepcopy(parent_a.genes)
        # Inherit half genes from B
        for k, v in parent_b.genes.items():
            if random.random() > 0.5:
                child_genes[k] = v

        child_source = (
            f"# [CROSSOVER: parents={parent_a.genome_id}, {parent_b.genome_id}]\n"
            + parent_a.ast_source
        )

        return ProgramGenome(
            genome_id=child_id,
            generation=gen,
            ast_source=child_source,
            genes=child_genes,
            mutations_applied=["crossover"],
            parent_ids=[parent_a.genome_id, parent_b.genome_id]
        )
