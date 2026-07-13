"""
Custom exceptions for the IRA system.
Every pillar raises these specific exceptions — never generic Exception.
"""
class IRABaseError(Exception):
    """Base exception for all IRA errors."""
    def __init__(self, message: str, pillar: str = "unknown",
                 details: dict = None):
        self.pillar = pillar
        self.details = details or {}
        super().__init__(f"[IRA.{pillar}] {message}")

class CacheMissError(IRABaseError):
    """Raised when a cache lookup fails to find a match."""
    def __init__(self, query: str, pillar: str = "qsm"):
        super().__init__(
            f"Cache miss for query: {query[:50]}...",
            pillar=pillar,
            details={"query_prefix": query[:100]}
        )

class ModelLoadError(IRABaseError):
    """Raised when a model fails to load."""
    def __init__(self, model_path: str, device: str, reason: str,
                 pillar: str = "pse"):
        super().__init__(
            f"Failed to load model '{model_path}' on '{device}': {reason}",
            pillar=pillar,
            details={"model_path": model_path, "device": device}
        )

class ComputeError(IRABaseError):
    """Raised when a computation fails."""
    def __init__(self, operation: str, reason: str,
                 pillar: str = "unknown"):
        super().__init__(
            f"Compute error in '{operation}': {reason}",
            pillar=pillar,
            details={"operation": operation}
        )

class ConfigurationError(IRABaseError):
    """Raised when configuration is invalid."""
    def __init__(self, parameter: str, reason: str):
        super().__init__(
            f"Invalid configuration for '{parameter}': {reason}",
            pillar="config",
            details={"parameter": parameter}
        )

class SpeculationError(ComputeError):
    """Raised when speculative decoding fails."""
    def __init__(self, reason: str):
        super().__init__("speculative_decoding", reason, pillar="pse")

class SymbolicExecutionError(ComputeError):
    """Raised when symbolic code execution fails."""
    def __init__(self, expression: str, reason: str):
        super().__init__(
            f"symbolic_exec('{expression[:50]}')",
            reason,
            pillar="nsf"
        )

class DeviceNotAvailableError(ModelLoadError):
    """Raised when requested compute device is not available."""
    def __init__(self, device: str, available_devices: list):
        super().__init__(
            "N/A", device,
            f"Device not available. Available: {available_devices}",
            pillar="hardware"
        )
