#!/usr/bin/env python3
"""
hyper.py
=============================================================================
LEO / HYPER — Computational Wormhole Discovery Engine
Master Command-Line Interface Driver
=============================================================================
Usage:
    python hyper.py inspect
    python hyper.py contract
    python hyper.py analyze
    python hyper.py necessity
    python hyper.py wormhole
    python hyper.py search
    python hyper.py verify
    python hyper.py falsify
    python hyper.py holdout
    python hyper.py benchmark
    python hyper.py certificate
    python hyper.py explain
"""

import sys
from hyper_x.cli import main

if __name__ == "__main__":
    main()
