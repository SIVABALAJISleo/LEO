def get_compute_node(load: float):
    """
    Routes compute based on deterministic load thresholds.
    """
    if load < 0.5:
        return "LOCAL_CPU"
    return "CLOUD_GPU"
