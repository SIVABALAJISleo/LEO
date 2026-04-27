from core.inference import run_inference

def execute_task(task_id: str, query: str):
    """
    Executes a task by routing through inference.
    """
    result = run_inference(query)
    return {"task_id": task_id, "result": result}
