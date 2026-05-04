class SmartRouter:
    """
    2️⃣ TASK CLASSIFIER + 3️⃣ SMART ROUTER
    Classify and route to specialized engines
    """
    def classify(self, user_input: str) -> str:
        input_lower = user_input.lower()
        if any(w in input_lower for w in ["calculate", "sum", "math", "equation"]):
            return "MATH"
        if any(w in input_lower for w in ["def ", "class ", "python", "code"]):
            return "CODE"
        if any(w in input_lower for w in ["find", "search", "lookup", "who is", "what is"]):
            return "RETRIEVAL"
        if any(w in input_lower for w in ["if ", "therefore", "logical", "constraint"]):
            return "LOGIC"
        return "GENERAL"

    def route(self, task_type: str) -> str:
        # Returns the optimal engine name for routing
        mapping = {
            "RETRIEVAL": "retrieval_engine",
            "MATH": "math_engine",
            "CODE": "code_engine",
            "LOGIC": "symbolic_engine",
            "GENERAL": "small_model"
        }
        return mapping.get(task_type, "small_model")
吐
