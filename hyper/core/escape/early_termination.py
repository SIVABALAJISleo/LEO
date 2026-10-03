"""
hyper/core/escape/early_termination.py
Breakthrough Engine B — Certified Early Termination (Prompt Section 8).
Computes conservative interval bounds [L_k, U_k] for decision contracts:
- argmax
- top-k
- threshold
Stops early only when the decision is mathematically certified:
    L_c > max_{k != c} U_k
Falls back to exact canonical execution if certification condition fails. Never guesses.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import numpy as np

from hyper.core.cost.ledger import AccountingType, WorkLedger
from hyper.core.proof.engine import ProofCertificate, ProofEngine


class CertifiedEarlyTerminationEngine:
    """
    Executes certified decision computation with bounded interval certificates.
    """

    @classmethod
    def compute_certified_argmax_gemv(
        cls,
        W: np.ndarray,
        x: np.ndarray,
        chunk_size: int = 16,
    ) -> Tuple[int, WorkLedger, Optional[ProofCertificate], bool]:
        """
        Computes argmax(W @ x) incrementally by computing partial inner products
        and bounding remaining residuals.
        W: (K, D), x: (D,)
        z_k = sum_{i=0}^{D-1} W[k, i] * x[i]
        """
        K, D = W.shape
        baseline_ops = 2 * K * D

        partial_sums = np.zeros(K, dtype=np.float64)
        total_ops = 0

        # Precompute Cauchy-Schwarz or L1 residual bounds for remaining coordinates
        # |sum_{i=d}^D W[k, i] * x[i]| <= norm(W[k, d:], 2) * norm(x[d:], 2)
        x_norms = np.array([np.linalg.norm(x[d:]) for d in range(0, D, chunk_size)])

        step = 0
        certified = False
        winner_idx = -1
        proof_cert = None

        for d_start in range(0, D, chunk_size):
            d_end = min(d_start + chunk_size, D)
            chunk_len = d_end - d_start

            # Partial inner product
            partial_sums += np.dot(W[:, d_start:d_end], x[d_start:d_end])
            total_ops += 2 * K * chunk_len

            # If all coordinates computed, exact argmax is reached
            if d_end == D:
                winner_idx = int(np.argmax(partial_sums))
                certified = True
                _, proof_cert = ProofEngine.prove_early_termination_argmax(
                    lower_bounds=partial_sums,
                    upper_bounds=partial_sums,
                    candidate_idx=winner_idx,
                )
                break

            # Compute conservative upper and lower bounds on final z_k
            rem_x_norm = x_norms[step + 1] if (step + 1) < len(x_norms) else 0.0
            W_rem_norms = np.linalg.norm(W[:, d_end:], axis=1)
            radius = W_rem_norms * rem_x_norm

            lower_bounds = partial_sums - radius
            upper_bounds = partial_sums + radius

            cand_idx = int(np.argmax(lower_bounds))
            is_provable, cert = ProofEngine.prove_early_termination_argmax(
                lower_bounds=lower_bounds,
                upper_bounds=upper_bounds,
                candidate_idx=cand_idx,
            )

            if is_provable:
                certified = True
                winner_idx = cand_idx
                proof_cert = cert
                break

            step += 1

        if not certified:
            # Fallback to full exact argmax
            z_full = np.dot(W, x)
            winner_idx = int(np.argmax(z_full))
            total_ops = baseline_ops
            eliminated = 0
        else:
            eliminated = max(0, baseline_ops - total_ops)

        ledger = WorkLedger(
            accounting_type=AccountingType.INSTRUMENTED,
            baseline_executed_operations=baseline_ops,
            candidate_executed_operations=total_ops,
            operations_eliminated=eliminated,
            memory_bytes_baseline=W.nbytes + x.nbytes,
            memory_bytes_candidate=total_ops * 4,
            verification_operations=K * 2,
        )

        return winner_idx, ledger, proof_cert, certified
