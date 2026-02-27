import numpy as np

class PerceptualValidationMetric:
    """
    Compares two frames using PSNR (Peak Signal-to-Noise Ratio).
    If PSNR >= threshold the result is 'good enough' — no GPU needed.
    """

    def __init__(self, psnr_threshold: float = 35.0):
        self.threshold = psnr_threshold

    def psnr(self, reference: np.ndarray, candidate: np.ndarray) -> float:
        ref = reference.astype(np.float64)
        can = candidate.astype(np.float64)
        mse = np.mean((ref - can) ** 2)
        if mse == 0:
            return float("inf")
        return 20 * np.log10(255.0 / np.sqrt(mse))

    def is_equivalent(self, reference: np.ndarray, candidate: np.ndarray):
        score = self.psnr(reference, candidate)
        return score >= self.threshold, score
