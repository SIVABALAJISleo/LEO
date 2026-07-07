"""
scripts/bench_hardware.py
Script wrapper to run LEO Layer 1 Silicon Awakening benchmarks and log comparison metrics.
"""

import os
import sys

sys.path.append(os.getcwd())

from backend.benchmarks import layer1_silicon_bench


def main():
    print("=" * 60)
    print("  LEO AI Hardware Acceleration Benchmark (Layer 1)")
    print("=" * 60)
    layer1_silicon_bench.main()


if __name__ == "__main__":
    main()
