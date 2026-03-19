"""
Feedback Store (Self-Learning)
Logs query success data to dynamically adjust thresholds.
"""
import json
import os

class FeedbackStore:
    def __init__(self, persistence_path: str = "feedback_state.json"):
        self.path = persistence_path
        self.state = self.load_state()

    def load_state(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"threshold": 0.7, "events": []}

    def log_event(self, query: str, confidence: float, success: bool):
        self.state["events"].append({"q": query, "c": float(confidence), "s": bool(success)})
        # Basic learning: if we have 5 successes in a row, drop threshold slightly
        last_events = self.state["events"][-5:]
        if len(last_events) == 5 and all(e["s"] for e in last_events):
            self.state["threshold"] = float(max(0.5, self.state["threshold"] - 0.01))
        # If any failure, spike threshold back up
        elif not success:
            self.state["threshold"] = float(min(0.9, self.state["threshold"] + 0.05))
        
        self.save_state()

    def get_threshold(self) -> float:
        return self.state["threshold"]

    def save_state(self):
        with open(self.path, "w") as f:
            json.dump(self.state, f)

global_feedback_store = FeedbackStore()
