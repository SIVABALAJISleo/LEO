"""
Adaptive Intelligence Controller (AIC)
The primary router facade that integrates the PolicyStore, DecisionEngine, and Feedback loops.
"""
from backend.intelligence.policy_store import global_policy_store
from backend.intelligence.decision_engine import DecisionEngine
from backend.intelligence.learning_engine import LearningEngine
from backend.intelligence.feedback_collector import FeedbackCollector

class AdaptiveController:
    def __init__(self):
        self.policy_store = global_policy_store
        self.decision_engine = DecisionEngine()
        self.learning_engine = LearningEngine()
        self.feedback_collector = FeedbackCollector()

    def route(self, features: dict) -> str:
        """Evaluates features against the current dynamic policy."""
        policy = self.policy_store.get()
        return self.decision_engine.decide(features, policy)

    def process_feedback(self, query: str, answer: str, success: bool, fallback_triggered: bool):
        """Integrates external feedback to adjust future routings."""
        feedback = self.feedback_collector.collect(query, answer, success, fallback_triggered)
        self.learning_engine.update(feedback, self.policy_store)

global_adaptive_controller = AdaptiveController()
