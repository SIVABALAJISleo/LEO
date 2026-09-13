#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/pathway_search/candidate.py
===================================
Phase 5: Candidate Computational Pathway Representation.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, Any, Optional, Tuple
import numpy as np


@dataclass
class CandidatePathway:
    candidate_id: str
    strategy_name: str                     # EXACT_REUSE, LOW_RANK_SVD, SPARSE_INDEXED, REFORMULATION, EXACT_REFERENCE
    description: str
    preconditions_met: bool
    execute_fn: Callable[[], Tuple[Any, Dict[str, Any]]]
    mathematical_assumptions: Dict[str, Any] = field(default_factory=dict)
    estimated_speedup: float = 1.0
    estimated_memory_reduction: float = 1.0
    work_elimination_pct: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
