"""
Cost Tracking Engine
Calculates compute savings for the SaaS product value prop.
"""

class CostTracker:
    # Industry standard estimates ($ per 1k tokens)
    COST_PER_1K_TOKENS = {
        "large_model": 0.03,  # e.g., GPT-4 class
        "small_model": 0.002, # e.g., GPT-3.5/Haiku class
        "tiny_model": 0.0005, # e.g., specialized micro models
        "hyper_optimization": 0.0 # Bypassed entirely
    }

    def estimate_savings(self, answer: str, model_used: str = "hyper_optimization") -> float:
        """
        Calculates how much money was saved by NOT using a Large Model.
        """
        # Rough token estimate (words * 1.3)
        token_count = len(answer.split()) * 1.3
        
        baseline_cost = (token_count / 1000) * self.COST_PER_1K_TOKENS["large_model"]
        actual_cost = (token_count / 1000) * self.COST_PER_1K_TOKENS.get(model_used, 0.0)
        
        savings = baseline_cost - actual_cost
        return round(max(0.0, savings), 5)

global_cost_tracker = CostTracker()
