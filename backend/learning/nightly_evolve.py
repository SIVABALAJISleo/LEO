"""
backend/learning/nightly_evolve.py
Standalone entry point for autonomous overnight evolution.

Usage:
    python -m backend.learning.nightly_evolve --generations 10
"""

from __future__ import annotations

import argparse
import logging
import sys
import os

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("nightly_evolve")


def main():
    parser = argparse.ArgumentParser(
        description="LEO AI Nightly Evolution — autonomous self-improvement loop"
    )
    parser.add_argument(
        "--generations", "-g",
        type=int,
        default=10,
        help="Number of evolution generations to run (default: 10)",
    )
    parser.add_argument(
        "--benchmark-path", "-b",
        type=str,
        default="reports/infinity_bench_results.json",
        help="Path to benchmark results JSON",
    )
    args = parser.parse_args()

    logger.info(f"Starting LEO Nightly Evolution: {args.generations} generations")
    logger.info(f"Benchmark source: {args.benchmark_path}")

    from backend.learning.self_improvement import InfinityEvolutionLoop

    loop = InfinityEvolutionLoop(config_path=args.benchmark_path)
    results = loop.run_nightly_loop(max_generations=args.generations)

    # Final summary
    final = results[-1] if results else {}
    logger.info(f"Nightly evolution complete. Final generation: {final.get('generation', 0)}")
    logger.info(f"Best fitness achieved: {loop._best_fitness:.6f}")
    logger.info(f"Evolution history saved to: reports/evolution_history.json")


if __name__ == "__main__":
    main()
