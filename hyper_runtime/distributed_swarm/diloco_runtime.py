import numpy as np

class DiLoCoRuntime:
    def __init__(self, num_workers=4, inner_steps=50):
        self.num_workers = num_workers
        self.inner_steps = inner_steps
        self.global_weights = np.random.randn(1024)
        
    def train_round(self):
        worker_updates = []
        for w in range(self.num_workers):
            local_weights = self.global_weights.copy()
            for _ in range(self.inner_steps):
                grad = np.random.randn(1024) * 0.1
                local_weights -= 0.01 * grad
            delta = local_weights - self.global_weights
            worker_updates.append(delta)
            
        avg_delta = np.mean(worker_updates, axis=0)
        self.global_weights += avg_delta
