"""
benchmarks/four_score_audit.py
LEO Master Scientific Audit Suite
Runs the 100% Real FAISS + SentenceTransformers Semantic Subsumption Benchmark
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from leo_real_engine import run_real_benchmark

if __name__ == "__main__":
    run_real_benchmark()
