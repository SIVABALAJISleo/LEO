import numpy as np
from typing import List, Callable, Any

class LazyTensor:
    """
    A tensor that delays computation to build an execution graph.
    This allows the Fusion Compiler to intercept intermediate operations
    and combine them into a single pass, avoiding memory materialization.
    """
    def __init__(self, data: np.ndarray = None, shape: tuple = None, base_data=None):
        self.data = data
        self.base_data = base_data if base_data is not None else data
        self.shape = shape if shape is not None else (data.shape if data is not None else None)
        self.operations = [] # List of tuples (op_type, args)
        
    def __add__(self, other):
        result = LazyTensor(shape=self.shape, base_data=self.base_data)
        result.operations = self.operations.copy()
        result.operations.append(("add", other))
        return result
        
    def __mul__(self, other):
        result = LazyTensor(shape=self.shape, base_data=self.base_data)
        result.operations = self.operations.copy()
        result.operations.append(("mul", other))
        return result
        
    def relu(self):
        result = LazyTensor(shape=self.shape, base_data=self.base_data)
        result.operations = self.operations.copy()
        result.operations.append(("relu", None))
        return result
        
    def realize(self):
        """Forces computation without fusion (Naive baseline)"""
        if self.base_data is None:
            raise ValueError("No base data to compute from.")
            
        current = self.base_data.copy()
        for op, arg in self.operations:
            if op == "add":
                current = current + (arg.data if isinstance(arg, LazyTensor) else arg)
            elif op == "mul":
                current = current * (arg.data if isinstance(arg, LazyTensor) else arg)
            elif op == "relu":
                current = np.maximum(current, 0)
        return current
