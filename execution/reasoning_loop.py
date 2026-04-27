from execution.execution import execute_task

def start_loop(query: str, steps: int = 1):
    """
    Deterministic step-sequencer for reasoning.
    """
    history = []
    for i in range(steps):
        res = execute_task(f"step_{i}", query)
        history.append(res)
    return history
