"""
algorithm_discovery: Autonomous discovery, synthesis, and evolutionary search
for alternative lower-complexity and contract-sufficient computational algorithms.
"""

from .generator import StrategyCandidateGenerator, AlgorithmStrategy
from .complexity_transformer import ComplexityTransformer
from .evolutionary_loop import EvolutionaryOptimizationLoop, CandidateIndividual

__all__ = [
    "StrategyCandidateGenerator",
    "AlgorithmStrategy",
    "ComplexityTransformer",
    "EvolutionaryOptimizationLoop",
    "CandidateIndividual",
]
