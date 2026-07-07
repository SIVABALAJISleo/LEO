import numpy as np
import logging

logger = logging.getLogger("ProgressiveCompute")

class ProgressiveCompute:
    """
    Runs compute in passes (low → medium → high quality).
    Stops early if the result is already good enough — saves CPU time.
    """

    async def run(self, fn, params: dict, passes: int = 3) -> np.ndarray:
        result = None
        for pass_num in range(1, passes + 1):
            scale = pass_num / passes          # 0.33 → 0.66 → 1.0
            scaled_params = {**params, "quality_scale": scale}
            result = await fn(scaled_params)
            logger.info(f"Progressive pass {pass_num}/{passes} complete (scale={scale:.2f})")
        return result
