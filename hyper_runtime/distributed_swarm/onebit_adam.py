import numpy as np

class OneBitAdam:
    def __init__(self, params, lr=1e-3):
        self.params = params
        self.lr = lr
        self.m = np.zeros_like(params)
        self.v = np.zeros_like(params)
        self.beta1 = 0.9
        self.beta2 = 0.999
        self.t = 0
        
    def compress(self, gradient):
        scale = np.mean(np.abs(gradient))
        sign_grad = np.sign(gradient)
        return sign_grad, scale

    def decompress(self, sign_grad, scale):
        return sign_grad * scale
        
    def step(self, grad_compressed, scale):
        self.t += 1
        g = self.decompress(grad_compressed, scale)
        
        self.m = self.beta1 * self.m + (1 - self.beta1) * g
        self.v = self.beta2 * self.v + (1 - self.beta2) * (g**2)
        
        m_hat = self.m / (1 - self.beta1**self.t)
        v_hat = self.v / (1 - self.beta2**self.t)
        
        self.params -= self.lr * m_hat / (np.sqrt(v_hat) + 1e-8)
        return self.params
