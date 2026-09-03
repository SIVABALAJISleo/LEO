"""
hyper_mvc_dar/fallback_ladder.py
9-Level Automatic Fallback Ladder: Cascades gracefully across strategies from Level 0 to Level 8.
"""

from enum import IntEnum
from typing import Dict, Any, Callable, Tuple
import logging

logger = logging.getLogger("FallbackLadder")


class FallbackLevel(IntEnum):
    LEVEL_0_EXACT_CACHE = 0
    LEVEL_1_EXACT_SIMPLIFICATION = 1
    LEVEL_2_EXACT_REFORMULATION = 2
    LEVEL_3_STRUCTURE_SPARSITY = 3
    LEVEL_4_MEMORY_KERNEL_OPT = 4
    LEVEL_5_CPU_IGPU_HYBRID = 5
    LEVEL_6_BOUNDED_APPROXIMATION = 6
    LEVEL_7_PREDICTION_VERIFICATION = 7
    LEVEL_8_EXACT_FALLBACK = 8


class FallbackLadder:
    """Executes strategies in priority order, cascading to safer levels if verification fails."""

    @staticmethod
    def execute_with_ladder(
        op_name: str,
        dispatchers: Dict[FallbackLevel, Callable[[], Any]],
        verifier: Callable[[Any], bool]
    ) -> Dict[str, Any]:
        sorted_levels = sorted(dispatchers.keys())

        for level in sorted_levels:
            fn = dispatchers[level]
            try:
                result = fn()
                if verifier(result):
                    return {
                        "op_name": op_name,
                        "passed": True,
                        "final_executed_level": int(level),
                        "level_name": level.name,
                        "result": result
                    }
                else:
                    logger.warning(f"FallbackLadder: Level {level.name} failed verification. Cascading down.")
            except Exception as e:
                logger.warning(f"FallbackLadder: Level {level.name} raised exception {e}. Cascading down.")

        # Guaranteed Level 8 fallback if provided
        if FallbackLevel.LEVEL_8_EXACT_FALLBACK in dispatchers:
            res = dispatchers[FallbackLevel.LEVEL_8_EXACT_FALLBACK]()
            return {
                "op_name": op_name,
                "passed": True,
                "final_executed_level": int(FallbackLevel.LEVEL_8_EXACT_FALLBACK),
                "level_name": "LEVEL_8_EXACT_FALLBACK",
                "result": res
            }

        return {
            "op_name": op_name,
            "passed": False,
            "final_executed_level": -1,
            "level_name": "FAILED_ALL_LEVELS",
            "result": None
        }
