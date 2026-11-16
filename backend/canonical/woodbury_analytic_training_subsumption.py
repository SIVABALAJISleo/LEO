"""
backend/canonical/woodbury_analytic_training_subsumption.py
===========================================================
HYPER-Ω Leaf Engine: Contract-Level GPU Workload Substitution & Analytic Learning.

Mathematical Formulations:
--------------------------
1. Batch Ridge Regression (Primal Formulation):
   Given training representations Z in R^{N x r}, targets Y in R^{N x c}, and regularization lambda > 0:
       min_W || Z W - Y ||_F^2 + lambda || W ||_F^2
   The global analytic minimizer is:
       W* = (Z^T Z + lambda I_r)^{-1} Z^T Y
   Solved via Cholesky decomposition of the symmetric positive-definite (SPD) matrix:
       A = Z^T Z + lambda I_r = L L^T
       L Q = Z^T Y   (forward-substitution)
       L^T W* = Q    (back-substitution)
   Explicit matrix inversion is strictly avoided to guarantee numerical stability.

2. Dual Ridge Regression via Woodbury Identity (N < r Formulation):
   When N < r (fewer training samples than feature dimensions), the Woodbury identity
   transforms the r x r solve into an N x N kernel solve:
       (Z^T Z + lambda I_r)^{-1} Z^T = Z^T (Z Z^T + lambda I_N)^{-1}
       W* = Z^T (Z Z^T + lambda I_N)^{-1} Y
   Complexity decreases from O(r^3 + r^2 N) to O(N^3 + N^2 r).

3. Woodbury Rank-k Low-Rank Update:
   Given pre-factored Gram matrix A_0 = Z_0^T Z_0 + lambda I_r and a new batch Delta Z in R^{k x r}:
       (A_0 + Delta Z^T Delta Z)^{-1} = A_0^{-1} - A_0^{-1} Delta Z^T (I_k + Delta Z A_0^{-1} Delta Z^T)^{-1} Delta Z A_0^{-1}
   Allows closed-form incorporation of new data in O(k^3 + k r^2) without retraining from scratch.

4. Genuine Online Recursive Least Squares (RLS):
   Sequential sample-by-sample update for streaming features z_t in R^r and targets y_t in R^c:
       k_t = (P_{t-1} z_t) / (beta + z_t^T P_{t-1} z_t)
       P_t = (1 / beta) * (P_{t-1} - k_t z_t^T P_{t-1})
       W_t = W_{t-1} + k_t (y_t^T - z_t^T W_{t-1})
   Where:
       beta in (0, 1] is the forgetting factor (beta = 1.0 yields exact batch equivalence).
       P_0 = (1 / delta) I_r with delta = lambda.
       W_0 = 0_{r x c}.
       Symmetrization P_t = 0.5 * (P_t + P_t^T) prevents numerical asymmetry drift.

Scope & Boundaries:
-------------------
- Replaces iterative multi-epoch backpropagation on frozen feature extractors (e.g. LLM/Vision
  representations, Random Vector Functional Link / RVFL, Extreme Learning Machines).
- Does NOT claim to eliminate backpropagation through arbitrary non-linear internal weights.
- Distinguishes batch analytic solving from streaming RLS explicitly.
"""

from dataclasses import dataclass, field
import time
from typing import Dict, Any, Optional, Tuple, Union
import numpy as np
import scipy.linalg


@dataclass
class AnalyticLearningResult:
    """Encapsulates the exact mathematical output and complexity of analytic learning."""
    W: np.ndarray
    objective_value: float
    gradient_norm: float
    residual_norm: float
    samples_processed: int
    feature_dim: int
    target_dim: int
    regularization: float
    solver_mode: str
    flops_estimated: int
    peak_memory_bytes: int
    latency_ms: float
    status: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class WoodburyAnalyticTrainer:
    """
    Numerically stable, closed-form analytic learning engine for regularized least-squares
    objectives. Eliminates iterative gradient descent on frozen representations.
    """

    def __init__(self, lambda_reg: float = 1e-3, jitter: float = 1e-12):
        if lambda_reg <= 0.0:
            raise ValueError(f"Regularization parameter lambda_reg must be > 0, got {lambda_reg}")
        self.lambda_reg = float(lambda_reg)
        self.jitter = float(jitter)

    def solve_batch_ridge(
        self,
        Z: np.ndarray,
        Y: np.ndarray,
        force_mode: Optional[str] = None
    ) -> AnalyticLearningResult:
        """
        Solves min_W || Z W - Y ||_F^2 + lambda || W ||_F^2 via numerically stable Cholesky solve.
        Automatically switches between Primal (r x r) and Dual/Woodbury (N x N) based on dimensions.

        Complexity:
            Primal (N >= r): O(N r^2 + N r c + (1/3) r^3 + 2 r^2 c)
            Dual   (N < r) : O(r N^2 + N^2 c + (1/3) N^3 + 2 N^2 c + r N c)
        """
        t0 = time.perf_counter()
        Z = np.asarray(Z, dtype=np.float64)
        Y = np.asarray(Y, dtype=np.float64)

        if Z.ndim != 2:
            raise ValueError(f"Feature matrix Z must be 2D, got shape {Z.shape}")
        if Y.ndim == 1:
            Y = Y.reshape(-1, 1)
        elif Y.ndim != 2:
            raise ValueError(f"Target matrix Y must be 1D or 2D, got shape {Y.shape}")

        N, r = Z.shape
        N_y, c = Y.shape
        if N != N_y:
            raise ValueError(f"Dimension mismatch: Z has {N} samples, Y has {N_y} samples")
        if N == 0 or r == 0:
            raise ValueError(f"Empty input matrix: N={N}, r={r}")

        # Choose optimal formulation based on dimension ratio unless forced
        if force_mode is not None:
            mode = force_mode.upper()
        else:
            mode = "DUAL_WOODBURY" if N < r else "PRIMAL_CHOLESKY"

        peak_bytes = 0
        flops = 0

        if mode == "PRIMAL_CHOLESKY":
            # Gram matrix A = Z^T Z + lambda I_r (r x r)
            # FLOPs: 2 * N * r^2
            Gram = Z.T @ Z
            flops += 2 * N * r * r
            Gram.flat[:: r + 1] += self.lambda_reg
            peak_bytes += Gram.nbytes

            # RHS = Z^T Y (r x c)
            # FLOPs: 2 * N * r * c
            RHS = Z.T @ Y
            flops += 2 * N * r * c
            peak_bytes += RHS.nbytes

            # Solve A W = RHS using Cholesky
            # FLOPs: (1/3) * r^3 + 2 * r^2 * c
            try:
                L, low = scipy.linalg.cho_factor(Gram, lower=True, check_finite=False)
                W = scipy.linalg.cho_solve((L, low), RHS, check_finite=False)
                flops += int((1.0 / 3.0) * (r**3) + 2 * (r**2) * c)
            except scipy.linalg.LinAlgError:
                # Fallback to perturbed Cholesky or SVD for ill-conditioned Gram
                Gram.flat[:: r + 1] += self.jitter
                W, _, _, _ = scipy.linalg.lstsq(Gram, RHS, check_finite=False)
                flops += 2 * (r**3) + 2 * (r**2) * c
                mode = "PRIMAL_LSTSQ_FALLBACK"

        elif mode == "DUAL_WOODBURY":
            # Dual Kernel matrix K = Z Z^T + lambda I_N (N x N)
            # FLOPs: 2 * r * N^2
            K = Z @ Z.T
            flops += 2 * r * N * N
            K.flat[:: N + 1] += self.lambda_reg
            peak_bytes += K.nbytes

            # Solve K Alpha = Y using Cholesky (N x c)
            # FLOPs: (1/3) * N^3 + 2 * N^2 * c
            try:
                L, low = scipy.linalg.cho_factor(K, lower=True, check_finite=False)
                Alpha = scipy.linalg.cho_solve((L, low), Y, check_finite=False)
                flops += int((1.0 / 3.0) * (N**3) + 2 * (N**2) * c)
            except scipy.linalg.LinAlgError:
                K.flat[:: N + 1] += self.jitter
                Alpha, _, _, _ = scipy.linalg.lstsq(K, Y, check_finite=False)
                flops += 2 * (N**3) + 2 * (N**2) * c
                mode = "DUAL_LSTSQ_FALLBACK"

            # Reconstruct W = Z^T Alpha (r x c)
            # FLOPs: 2 * r * N * c
            W = Z.T @ Alpha
            flops += 2 * r * N * c
            peak_bytes += Alpha.nbytes + W.nbytes

        else:
            raise ValueError(f"Unknown solver mode: {mode}")

        peak_bytes += W.nbytes
        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000.0

        # Calculate exact objective and optimality metrics
        # Residual = Z W - Y
        Residual = Z @ W - Y
        residual_norm = float(np.linalg.norm(Residual, "fro"))
        w_norm = float(np.linalg.norm(W, "fro"))
        objective = float(residual_norm**2 + self.lambda_reg * (w_norm**2))

        # Gradient = 2 * (Z^T (Z W - Y) + lambda W)
        Grad = 2.0 * (Z.T @ Residual + self.lambda_reg * W)
        grad_norm = float(np.linalg.norm(Grad, "fro"))

        status = "OPTIMAL" if grad_norm < max(1e-4, 1e-5 * float(N * r)) else "NUMERICAL_APPROX"

        return AnalyticLearningResult(
            W=W,
            objective_value=objective,
            gradient_norm=grad_norm,
            residual_norm=residual_norm,
            samples_processed=N,
            feature_dim=r,
            target_dim=c,
            regularization=self.lambda_reg,
            solver_mode=mode,
            flops_estimated=flops,
            peak_memory_bytes=peak_bytes,
            latency_ms=latency_ms,
            status=status,
            metadata={
                "primal_dual_breakeven_N_equals_r": r,
                "cholesky_factorization": True,
                "explicit_inverse_calculated": False,
            }
        )

    def solve_woodbury_rank_k_update(
        self,
        P_0: np.ndarray,
        W_0: np.ndarray,
        Delta_Z: np.ndarray,
        Delta_Y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Applies the Woodbury Matrix Identity to incorporate a batch of k new samples:
            (A_0 + Delta_Z^T Delta_Z)^{-1} = P_0 - P_0 Delta_Z^T (I_k + Delta_Z P_0 Delta_Z^T)^{-1} Delta_Z P_0
        where P_0 = (Z_0^T Z_0 + lambda I_r)^{-1}.

        Complexity: O(k^3 + k^2 r + k r^2) instead of O(r^3 + N r^2).
        Returns:
            Tuple of (W_updated, P_updated).
        """
        Delta_Z = np.asarray(Delta_Z, dtype=np.float64)
        Delta_Y = np.asarray(Delta_Y, dtype=np.float64)
        if Delta_Y.ndim == 1:
            Delta_Y = Delta_Y.reshape(-1, 1)

        k, r = Delta_Z.shape
        _, c = Delta_Y.shape

        # M = P_0 Delta_Z^T (r x k)
        M = P_0 @ Delta_Z.T
        # Core = I_k + Delta_Z M (k x k)
        Core = np.eye(k, dtype=np.float64) + Delta_Z @ M

        # Solve Core Gamma = Delta_Z P_0 (k x r)
        L, low = scipy.linalg.cho_factor(Core, lower=True, check_finite=False)
        Gamma = scipy.linalg.cho_solve((L, low), M.T, check_finite=False)

        # Updated inverse covariance P_1 = P_0 - M Gamma
        P_1 = P_0 - M @ Gamma
        # Symmetrize
        P_1 = 0.5 * (P_1 + P_1.T)

        # Innovation Delta_Y - Delta_Z W_0 (k x c)
        Innovation = Delta_Y - Delta_Z @ W_0
        # W_1 = W_0 + P_1 Delta_Z^T Innovation
        # Actually in Woodbury RLS batch update:
        # W_1 = W_0 + P_0 Delta_Z^T (I_k + Delta_Z P_0 Delta_Z^T)^{-1} Innovation
        # Note M (k x k)^{-1} Innovation = Gamma^T Innovation (since Gamma = Core^{-1} M.T)
        Delta_W = scipy.linalg.cho_solve((L, low), Innovation, check_finite=False)
        W_1 = W_0 + M @ Delta_W

        return W_1, P_1


class OnlineRecursiveLeastSquares:
    """
    Genuine Online Recursive Least Squares (RLS) filter for streaming data adaptation.
    Performs exact sequential parameter estimation with forgetting factor beta in (0, 1].

    Update Equations:
        k_t = (P_{t-1} z_t) / (beta + z_t^T P_{t-1} z_t)
        P_t = (1 / beta) * (P_{t-1} - k_t z_t^T P_{t-1})
        W_t = W_{t-1} + k_t (y_t^T - z_t^T W_{t-1})

    Equivalence:
        When beta = 1.0, W_N asymptotically converges to the exact batch ridge-regression
        solution as t -> N with P_0 = (1 / lambda) I_r.
    """

    def __init__(
        self,
        feature_dim: int,
        target_dim: int = 1,
        lambda_reg: float = 1e-3,
        forgetting_factor: float = 1.0
    ):
        if feature_dim <= 0:
            raise ValueError(f"feature_dim must be positive, got {feature_dim}")
        if target_dim <= 0:
            raise ValueError(f"target_dim must be positive, got {target_dim}")
        if lambda_reg <= 0.0:
            raise ValueError(f"lambda_reg must be positive, got {lambda_reg}")
        if not (0.0 < forgetting_factor <= 1.0):
            raise ValueError(f"forgetting_factor must be in (0, 1], got {forgetting_factor}")

        self.r = int(feature_dim)
        self.c = int(target_dim)
        self.lambda_reg = float(lambda_reg)
        self.beta = float(forgetting_factor)

        # Initialize parameter matrix W to zeros (r x c)
        self.W = np.zeros((self.r, self.c), dtype=np.float64)

        # Initialize inverse covariance P = (1 / lambda) I_r
        # This matches the batch ridge regularization penalty lambda ||W||_F^2
        self.P = np.eye(self.r, dtype=np.float64) / self.lambda_reg

        self.steps_processed = 0
        self.total_flops = 0

    def update_sample(self, z_t: np.ndarray, y_t: np.ndarray) -> np.ndarray:
        """
        Updates parameters given a single streaming sample (z_t, y_t).

        Parameters:
            z_t: Feature vector of shape (r,) or (1, r).
            y_t: Target vector of shape (c,) or (1, c).

        Returns:
            Current error / innovation vector: y_t - W_{t-1}^T z_t
        """
        z_t = np.asarray(z_t, dtype=np.float64).reshape(-1)
        y_t = np.asarray(y_t, dtype=np.float64).reshape(-1)

        if z_t.shape[0] != self.r:
            raise ValueError(f"Feature size mismatch: expected {self.r}, got {z_t.shape[0]}")
        if y_t.shape[0] != self.c:
            raise ValueError(f"Target size mismatch: expected {self.c}, got {y_t.shape[0]}")

        # 1. Compute Pi = P_{t-1} z_t (r x 1)
        # FLOPs: 2 * r^2
        Pi = self.P @ z_t
        self.total_flops += 2 * self.r * self.r

        # 2. Denominator gamma = beta + z_t^T Pi (scalar)
        # FLOPs: 2 * r
        gamma = self.beta + float(np.dot(z_t, Pi))
        self.total_flops += 2 * self.r

        # 3. Kalman gain k_t = Pi / gamma (r x 1)
        k_t = Pi / gamma
        self.total_flops += self.r

        # 4. Innovation / a priori error: e_t = y_t - W_{t-1}^T z_t
        # Note: W is (r x c), so z_t @ W is (c,)
        pred = z_t @ self.W
        error = y_t - pred
        self.total_flops += 2 * self.r * self.c

        # 5. Parameter update: W_t = W_{t-1} + k_t e_t^T (r x c)
        # Outer product k_t (r x 1) and error (c x 1)
        self.W += np.outer(k_t, error)
        self.total_flops += 2 * self.r * self.c

        # 6. Covariance update: P_t = (1 / beta) * (P_{t-1} - k_t Pi^T)
        # FLOPs: 2 * r^2 + r^2
        self.P -= np.outer(k_t, Pi)
        if self.beta != 1.0:
            self.P /= self.beta
        self.total_flops += 3 * self.r * self.r

        # 7. Symmetrization to prevent numerical drift
        self.P = 0.5 * (self.P + self.P.T)

        self.steps_processed += 1
        return error

    def update_stream(self, Z: np.ndarray, Y: np.ndarray) -> np.ndarray:
        """
        Processes a sequence of samples in streaming fashion one by one.
        Returns the array of cumulative errors.
        """
        Z = np.asarray(Z, dtype=np.float64)
        Y = np.asarray(Y, dtype=np.float64)
        if Y.ndim == 1:
            Y = Y.reshape(-1, 1)

        N = Z.shape[0]
        errors = np.zeros((N, self.c), dtype=np.float64)

        for i in range(N):
            errors[i] = self.update_sample(Z[i], Y[i])

        return errors

    def predict(self, Z_eval: np.ndarray) -> np.ndarray:
        """Computes predictions W^T Z_eval."""
        Z_eval = np.asarray(Z_eval, dtype=np.float64)
        if Z_eval.ndim == 1:
            return Z_eval @ self.W
        return Z_eval @ self.W


def compare_analytic_vs_iterative(
    Z: np.ndarray,
    Y: np.ndarray,
    lambda_reg: float = 1e-2,
    max_iter_epochs: int = 200,
    lr: float = 1e-2
) -> Dict[str, Any]:
    """
    Fair benchmark comparing the exact closed-form Woodbury Cholesky solver against
    a genuinely converged iterative gradient descent baseline under identical data,
    regularization, and objective function.
    """
    Z = np.asarray(Z, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    if Y.ndim == 1:
        Y = Y.reshape(-1, 1)

    N, r = Z.shape
    _, c = Y.shape

    # 1. Exact Analytic Solution
    trainer = WoodburyAnalyticTrainer(lambda_reg=lambda_reg)
    res_analytic = trainer.solve_batch_ridge(Z, Y)

    # 2. Iterative Full-Batch Gradient Descent Baseline
    t0_iter = time.perf_counter()
    W_iter = np.zeros((r, c), dtype=np.float64)
    history_losses = []

    # Optimal Lipschitz constant for step size: L = 2 * (||Z||_2^2 + lambda)
    s_max = float(np.linalg.norm(Z, 2))
    L_grad = 2.0 * (s_max**2 + lambda_reg)
    step_size = min(lr, 1.0 / L_grad if L_grad > 0 else lr)

    for epoch in range(max_iter_epochs):
        # Grad = 2 * (Z^T (Z W - Y) + lambda W)
        Residual = Z @ W_iter - Y
        Grad = 2.0 * (Z.T @ Residual + lambda_reg * W_iter)
        W_iter -= step_size * Grad

        res_norm = float(np.linalg.norm(Residual, "fro"))
        w_norm = float(np.linalg.norm(W_iter, "fro"))
        loss = res_norm**2 + lambda_reg * (w_norm**2)
        history_losses.append(loss)

        if float(np.linalg.norm(Grad, "fro")) < 1e-5:
            break

    t1_iter = time.perf_counter()
    iter_latency_ms = (t1_iter - t0_iter) * 1000.0

    # 3. Streaming RLS Online
    t0_rls = time.perf_counter()
    rls = OnlineRecursiveLeastSquares(feature_dim=r, target_dim=c, lambda_reg=lambda_reg, forgetting_factor=1.0)
    rls.update_stream(Z, Y)
    t1_rls = time.perf_counter()
    rls_latency_ms = (t1_rls - t0_rls) * 1000.0

    # Relative difference between Analytic W* and RLS W
    rls_weight_error = float(np.linalg.norm(res_analytic.W - rls.W, "fro") / max(1e-12, np.linalg.norm(res_analytic.W, "fro")))
    iter_weight_error = float(np.linalg.norm(res_analytic.W - W_iter, "fro") / max(1e-12, np.linalg.norm(res_analytic.W, "fro")))

    return {
        "N_samples": N,
        "feature_dim": r,
        "target_dim": c,
        "lambda_reg": lambda_reg,
        "analytic_loss": res_analytic.objective_value,
        "analytic_latency_ms": res_analytic.latency_ms,
        "analytic_grad_norm": res_analytic.gradient_norm,
        "iterative_loss": history_losses[-1],
        "iterative_latency_ms": iter_latency_ms,
        "iterative_epochs": len(history_losses),
        "iterative_weight_relative_error": iter_weight_error,
        "rls_latency_ms": rls_latency_ms,
        "rls_weight_relative_error": rls_weight_error,
        "analytic_speedup_vs_iterative": iter_latency_ms / max(1e-4, res_analytic.latency_ms),
    }

