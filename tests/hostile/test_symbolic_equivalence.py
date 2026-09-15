"""
tests/hostile/test_symbolic_equivalence.py
==========================================
Symbolic Equivalence Attack (Phases 3 & 33).
Tests symbolic collapse on invalid candidates and arbitrary domains.
Ensures verifier rejects non-equivalent expressions.
"""

import numpy as np
import pytest
from hyper_x.leaf.symbolic import (
    SymExpr,
    EquivalenceProver,
    ClosedFormSolver,
)


def test_symbolic_equivalence_rejection():
    prover = EquivalenceProver()

    # Reference: sum_{i=1}^N i
    ref_expr = SymExpr.summation(
        idx_var="i",
        lower=SymExpr.const(1),
        upper=SymExpr.var("N"),
        body=SymExpr.var("i"),
    )

    # Valid candidate: N * (N + 1) / 2
    valid_cand = SymExpr.div(
        SymExpr.mul(SymExpr.var("N"), SymExpr.add(SymExpr.var("N"), SymExpr.const(1))),
        SymExpr.const(2),
    )

    # Invalid candidate: N * N (wrong closed form)
    invalid_cand = SymExpr.mul(SymExpr.var("N"), SymExpr.var("N"))

    test_domain = [1, 2, 5, 10, 20]

    # Valid candidate must pass
    is_eq, max_err, _ = prover.prove_equivalence(ref_expr, valid_cand, "N", test_domain)
    assert is_eq is True
    assert max_err == 0.0

    # Invalid candidate MUST be rejected
    is_eq_bad, max_err_bad, report = prover.prove_equivalence(ref_expr, invalid_cand, "N", test_domain)
    assert is_eq_bad is False
    assert "FALSIFIED" in report
