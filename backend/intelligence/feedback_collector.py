"""
Feedback Collector
Collects metrics on answer success rates to feed back into the learning engine.
"""

class FeedbackCollector:
    """
    Simulates capturing user behavior (likes, dislikes, dwell time, regeneration requests)
    to determine if a bypassed model answer was actually successful.
    """
    def collect(self, query: str, answer: str, success: bool, fallback_triggered: bool) -> dict:
        return {
            "query": query,
            "answer_length": len(str(answer).split()),
            "success": success,
            "fallback_triggered": fallback_triggered
        }
