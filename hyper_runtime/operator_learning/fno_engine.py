import numpy as np

class FourierNeuralOperator:
    """
    Implements a fast approximation of PDEs/Simulation using Fourier Neural Operators.
    Learns the operator mapping in the frequency domain.
    """
    def __init__(self, modes=16, width=64):
        self.modes = modes
        self.width = width
        self.weights = np.random.randn(modes, width) + 1j * np.random.randn(modes, width)
        
    def spectral_conv(self, x):
        """
        x: [spatial_dim, channels]
        1D Fourier transform -> multiply weights -> Inverse Fourier
        """
        x_ft = np.fft.rfft(x, axis=0)
        out_ft = np.zeros_like(x_ft)
        modes_to_keep = min(self.modes, x_ft.shape[0])
        
        out_ft[:modes_to_keep, :] = x_ft[:modes_to_keep, :] * self.weights[:modes_to_keep, :x.shape[1]]
        x_out = np.fft.irfft(out_ft, n=x.shape[0], axis=0)
        return x_out
