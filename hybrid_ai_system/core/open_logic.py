class OpenSystem:
    """
    2. OPEN SYSTEM (LLM)
    - Generate k=3 candidate solutions
    - Fast, creative, flexible
    """
    def __init__(self, model_manager):
        self.models = model_manager

    async def propose(self, task: str, constraints: str) -> list:
        prompt = f"Task: {task}\nConstraints: {constraints}\nCode:\n```python\n"
        return self.models.generate(prompt, k=3)
