import logging

logger = logging.getLogger("FallbackGraph")

class FallbackGraph:
    """
    Tries the primary task; if it fails, walks the fallback chain automatically.
    """

    def __init__(self):
        self._tasks    = {}   # name -> coroutine function
        self._fallbacks = {}  # name -> [fallback_name, ...]

    def register_task(self, name: str, fn, fallbacks: list = None):
        self._tasks[name]     = fn
        self._fallbacks[name] = fallbacks or []

    async def execute(self, name: str, params: dict) -> dict:
        chain = [name] + self._fallbacks.get(name, [])

        for task_name in chain:
            fn = self._tasks.get(task_name)
            if fn is None:
                logger.warning(f"Task '{task_name}' not registered, skipping.")
                continue
            try:
                logger.info(f"Attempting task: {task_name}")
                result = await fn(params)
                return {"path": task_name, "status": "SUCCESS", "result": result}
            except Exception as e:
                logger.warning(f"Task '{task_name}' failed: {e}. Trying next fallback...")

        return {"path": "all_failed", "status": "FAILED", "result": None}
