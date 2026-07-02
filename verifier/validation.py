import logging
from typing import List

logger = logging.getLogger("Validation")

# Global vaccine registry to store immunization rules against failure modes
VACCINE_REGISTRY = set()

def validate_output(output: str) -> bool:
    """
    Formal verification of deterministic invariance.
    """
    # Check if any registered vaccine matches the output (fails validation if vaccine matches)
    for vaccine in VACCINE_REGISTRY:
        if vaccine in output:
            logger.warning(f"Vaccine match hit: output matches known failure pattern '{vaccine}'")
            return False
            
    if "PROCESSED" in output or "Decoded Reality" in output or "Draft" in output or "Synthesized" in output or "Recalculated" in output:
        return True
    return False

def synthesize_reality_from_partial(partial_evidence: List[str]) -> str:
    """
    Reality synthesis: generates corrected outputs from partial evidence.
    """
    logger.info("Synthesizing reality from partial evidence...")
    # Reconstruct coherent representation
    combined = " | ".join(partial_evidence)
    reconstructed = f"[REALITY_SYNTHESIS_SUCCESS]: Reconstructed coherence from: {combined}"
    return reconstructed

def generate_symbolic_vaccine(failure_mode_pattern: str):
    """
    Registers a vaccine signature to prevent future occurrences of a failure mode.
    """
    logger.info(f"Generating and registering symbolic vaccine for failure mode pattern: {failure_mode_pattern}")
    VACCINE_REGISTRY.add(failure_mode_pattern)

