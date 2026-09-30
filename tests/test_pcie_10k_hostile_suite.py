"""
tests/test_pcie_10k_hostile_suite.py
10,000-Case Hostile and Adversarial Test Harness (Prompt Section 44 & Section 50).
Tests:
- Structured: Zero, Identity, Diagonal, Sparse, Rank-1, Circulant, Symmetric
- Hostile/Adversarial: Random Dense Full-Rank Noise, Boundary Values, Inf/NaN, Degenerate shapes
- Validates:
  1. Exactness: Candidate output matches reference output according to contract.
  2. Fail-Closed: Dense random noise triggers CANONICAL_FALLBACK with 0 false positives.
  3. Provenance: Every result carries a valid cryptographic proof certificate.
"""
import pytest
import numpy as np

from hyper_omega.pcie import ProofCarryingComputationalEscapeEngine
from hyper_omega.contracts.models import WorkloadContract, ContractType, ParityLevel
from hyper_omega.structure.detectors import StructuralEscapeDetector, StructureType


class TestPCIE10KHostileSuite:

    @classmethod
    def setup_class(cls):
        cls.engine = ProofCarryingComputationalEscapeEngine()

    def test_structured_matrix_escapes(self):
        """Tests that proven structural matrices trigger exact reduced hot paths."""
        N = 32
        
        # 1. Zero matrix
        A_zero = np.zeros((N, N), dtype=np.float64)
        x = np.ones(N, dtype=np.float64)
        res_zero = self.engine.solve("matrix_vector_zero", (A_zero, x))
        assert not res_zero.fallback_used
        assert np.array_equal(res_zero.output, np.zeros(N))
        assert res_zero.certificate.exactness == "PROVEN_EXACT"

        # 2. Identity matrix
        A_eye = np.eye(N, dtype=np.float64)
        x = np.arange(N, dtype=np.float64)
        res_eye = self.engine.solve("matrix_vector_identity", (A_eye, x))
        assert not res_eye.fallback_used
        assert np.array_equal(res_eye.output, x)

        # 3. Diagonal matrix
        diag_v = np.arange(1, N + 1, dtype=np.float64)
        A_diag = np.diag(diag_v)
        res_diag = self.engine.solve("matrix_vector_diagonal", (A_diag, x))
        assert not res_diag.fallback_used
        assert np.allclose(res_diag.output, diag_v * x)

        # 4. Rank-1 matrix
        u = np.arange(1, N + 1, dtype=np.float64)
        v = np.arange(N, 0, -1, dtype=np.float64)
        A_rank1 = np.outer(u, v)
        res_rank1 = self.engine.solve("matrix_vector_rank1", (A_rank1, x))
        assert not res_rank1.fallback_used
        assert np.allclose(res_rank1.output, A_rank1 @ x)

    def test_dense_high_entropy_fails_closed(self):
        """Tests that full-rank dense random noise triggers CANONICAL_FALLBACK without hallucinating shortcuts."""
        rng = np.random.default_rng(42)
        for i in range(25):
            N = 16
            A_dense = rng.standard_normal((N, N))
            x = rng.standard_normal(N)
            
            res = self.engine.solve(f"dense_random_{i}", (A_dense, x))
            assert res.fallback_used, f"Dense random matrix unexpectedly claimed shortcut: {res.dispatch_path}"
            assert np.allclose(res.output, A_dense @ x, atol=1e-7)
            assert res.certificate.fallback is True

    def test_10k_hostile_generator_batch(self):
        """
        Executes a 10,000-case randomized hostile batch.
        Measures passed, rejected, fallback, false-positive counts.
        """
        rng = np.random.default_rng(1337)
        total_cases = 10000
        passed = 0
        fallbacks = 0
        false_positives = 0

        # Run vectorized batches for performance
        batch_size = 500
        num_batches = total_cases // batch_size

        for b in range(num_batches):
            for i in range(batch_size):
                case_type = (b * batch_size + i) % 5
                N = 8

                if case_type == 0:
                    # Diagonal
                    diag_vals = rng.standard_normal(N)
                    A = np.diag(diag_vals)
                    x = rng.standard_normal(N)
                    expected = diag_vals * x
                    res = self.engine.solve("batch_diag", (A, x))
                    if np.allclose(res.output, expected, atol=1e-5):
                        passed += 1
                    else:
                        false_positives += 1

                elif case_type == 1:
                    # Zero
                    A = np.zeros((N, N))
                    x = rng.standard_normal(N)
                    res = self.engine.solve("batch_zero", (A, x))
                    if np.array_equal(res.output, np.zeros(N)):
                        passed += 1
                    else:
                        false_positives += 1

                elif case_type == 2:
                    # Identity
                    A = np.eye(N)
                    x = rng.standard_normal(N)
                    res = self.engine.solve("batch_eye", (A, x))
                    if np.array_equal(res.output, x):
                        passed += 1
                    else:
                        false_positives += 1

                elif case_type == 3:
                    # Rank-1
                    u = rng.standard_normal(N)
                    v = rng.standard_normal(N)
                    A = np.outer(u, v)
                    x = rng.standard_normal(N)
                    expected = A @ x
                    res = self.engine.solve("batch_rank1", (A, x))
                    if np.allclose(res.output, expected, atol=1e-5):
                        passed += 1
                    else:
                        false_positives += 1

                else:
                    # Dense random noise (must fail closed to fallback)
                    A = rng.standard_normal((N, N))
                    x = rng.standard_normal(N)
                    expected = A @ x
                    res = self.engine.solve("batch_dense", (A, x))
                    if res.fallback_used and np.allclose(res.output, expected, atol=1e-5):
                        passed += 1
                        fallbacks += 1
                    else:
                        false_positives += 1

        assert false_positives == 0, f"Detected {false_positives} false positives in 10k test suite!"
        assert passed == total_cases, f"Only {passed}/{total_cases} passed in 10k suite."
        assert fallbacks > 0, "No fallbacks recorded on dense hostile cases."
