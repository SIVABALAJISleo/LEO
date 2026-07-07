import psutil

class AdaptiveDowngradeEngine:
    """
    Reads real CPU/RAM load and picks the right compute strategy.
    No GPU required — pure software intelligence.
    """

    TIERS = ["full", "perceptual", "cached", "template"]

    def get_quality_strategy(self, task_priority: str = "normal") -> dict:
        cpu    = psutil.cpu_percent(interval=0.2)
        ram    = psutil.virtual_memory().percent

        # Pick tier based on real system load
        if cpu < 50 and ram < 70:
            tier = "full"
        elif cpu < 75 or task_priority == "normal":
            tier = "perceptual"
        elif cpu < 90:
            tier = "cached"
        else:
            tier = "template"

        return {
            "tier":         tier,
            "cpu_load":     cpu,
            "ram_load":     ram,
            "reason":       f"CPU={cpu:.0f}% RAM={ram:.0f}%",
        }
