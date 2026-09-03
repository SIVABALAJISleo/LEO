"""
scripts/hyper3_cli.py
Standalone CLI entry point for HYPER 3.0.
"""

import sys
import os

# Ensure repo root is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hyper_v3.cli.hyper3_cli import main

if __name__ == "__main__":
    main()
