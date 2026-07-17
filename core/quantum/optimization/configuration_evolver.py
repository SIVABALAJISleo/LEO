"""
LEO Configuration Evolver
Uses a genetic algorithm to optimize core performance parameters.
"""
import random
from typing import Dict, List, Any

class ConfigurationEvolver:
    """
    Evolves quantum system configurations (e.g. cache thresholds, thread allocation sizes) to maximize throughput.
    """
    
    def __init__(self, population_size: int = 10):
        self.population_size = population_size
        self.population = [self._generate_random_config() for _ in range(population_size)]
        
    def _generate_random_config(self) -> Dict[str, Any]:
        return {
            'cpu_threads': random.randint(4, 12),
            'similarity_threshold': round(random.uniform(0.75, 0.95), 2),
            'max_active_experts': random.randint(2, 6),
            'num_draft_tokens': random.randint(3, 7)
        }
        
    def evolve(self, fitness_scores: List[float]) -> Dict[str, Any]:
        """Runs one generation of reproduction/mutation and returns the fittest candidate configuration"""
        # Zip configs and scores, sort by fitness descending
        ranked = sorted(zip(self.population, fitness_scores), key=lambda x: x[1], reverse=True)
        best_parent = ranked[0][0]
        
        # Reproduce with mutations
        new_population = [best_parent] # Elitism
        for _ in range(self.population_size - 1):
            child = {
                'cpu_threads': max(4, min(12, best_parent['cpu_threads'] + random.choice([-1, 0, 1]))),
                'similarity_threshold': max(0.70, min(0.99, round(best_parent['similarity_threshold'] + random.choice([-0.02, 0.0, 0.02]), 2))),
                'max_active_experts': max(2, min(8, best_parent['max_active_experts'] + random.choice([-1, 0, 1]))),
                'num_draft_tokens': max(2, min(10, best_parent['num_draft_tokens'] + random.choice([-1, 0, 1])))
            }
            new_population.append(child)
            
        self.population = new_population
        return best_parent
