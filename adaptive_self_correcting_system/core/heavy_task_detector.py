class HeavyTaskDetector:
    """
    1️⃣ TASK ANALYSIS ENGINE
    2️⃣ HEAVY TASK DETECTOR
    Detect: large datasets, real-time, image/video, massive search spaces
    """
    def check(self, user_input: str) -> str:
        input_lower = user_input.lower()
        
        # Keywords indicating heavy compute
        heavy_patterns = [
            "dataset", "video", "render", "simulate all", 
            "brute force", "train model", "high resolution",
            "search every", "massive"
        ]
        
        if any(p in input_lower for p in heavy_patterns) or len(user_input) > 2000:
            return "HEAVY"
            
        return "NORMAL"

