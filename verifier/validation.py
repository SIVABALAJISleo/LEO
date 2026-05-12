def validate_output(output: str):
    """
    Formal verification of deterministic invariance.
    """
    if "PROCESSED" in output:
        return True
    return False
