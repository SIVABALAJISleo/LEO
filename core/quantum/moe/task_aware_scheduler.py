"""
LEO Task-Aware Expert Scheduler
Sequences and optimizes expert execution paths depending on task profiles.
"""
from typing import List, Dict, Any

class TaskAwareScheduler:
    """
    Optimizes computation sequence by batching similar task requests together,
    avoiding excessive thrashing/swapping of active expert layers.
    """
    
    def __init__(self, buffer_size: int = 16):
        self.buffer_size = buffer_size
        self.task_buffer = []
        
    def add_task(self, query: str, task_type: str, input_data: Any):
        """Append task request to buffer for sequencing"""
        self.task_buffer.append({
            'query': query,
            'task_type': task_type,
            'input': input_data
        })
        
    def get_optimized_batch(self) -> List[Dict[str, Any]]:
        """Reorders buffered tasks to group similar task types together, reducing swap overhead"""
        if not self.task_buffer:
            return []
            
        # Group by task_type
        grouped = {}
        for task in self.task_buffer:
            tt = task['task_type']
            if tt not in grouped:
                grouped[tt] = []
            grouped[tt].append(task)
            
        # Flatten back into list
        ordered_tasks = []
        for tt in sorted(grouped.keys()):
            ordered_tasks.extend(grouped[tt])
            
        self.task_buffer = []
        return ordered_tasks
