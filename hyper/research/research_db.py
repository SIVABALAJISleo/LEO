"""
hyper/research/research_db.py
=============================
Academic Literature & Prior Art Research Database (1980s -> Present):
Catalogs algorithmic techniques, complexity bounds, and mathematical foundations.
"""

from typing import Dict, Any, List


class ResearchDatabase:
    """
    Registry of mathematical prior art and complexity bounds.
    """
    def __init__(self):
        self._entries = [
            {
                "technique": "Randomized SVD",
                "year": 2011,
                "authors": "Halko, Martinsson, Tropp",
                "source": "SIAM Review 53(2)",
                "claimed_complexity": "O(M * N * k)",
                "contract_class": "BOUNDED_ERROR",
                "verified": True
            },
            {
                "technique": "1.58-Bit LLM Multiplier-Free Quantization",
                "year": 2024,
                "authors": "Wang et al.",
                "source": "arXiv:2402.17764 (BitNet b1.58)",
                "claimed_complexity": "Zero float multiplies (addition-only LUT)",
                "contract_class": "APPLICATION",
                "verified": True
            },
            {
                "technique": "Simple & Practical Sparse Fast Fourier Transform",
                "year": 2012,
                "authors": "Hassanieh, Indyk, Katabi, Price",
                "source": "ACM-SIAM SODA",
                "claimed_complexity": "O(k log N)",
                "contract_class": "REDUCED_WORK",
                "verified": True
            },
            {
                "technique": "Fast Multipole Method for Particle Simulations",
                "year": 1987,
                "authors": "Greengard & Rokhlin",
                "source": "Journal of Computational Physics 73(2)",
                "claimed_complexity": "O(N)",
                "contract_class": "BOUNDED_ERROR",
                "verified": True
            },
            {
                "technique": "HyperLogLog Stream Cardinality Estimation",
                "year": 2007,
                "authors": "Flajolet, Fusy, Gandouet, Meunier",
                "source": "DMTCS",
                "claimed_complexity": "O(1) space, error <= 1.04/sqrt(m)",
                "contract_class": "BOUNDED_ERROR",
                "verified": True
            },
            {
                "technique": "Fast Inference via Speculative Decoding",
                "year": 2023,
                "authors": "Leviathan, Kalman, Matias",
                "source": "ICML",
                "claimed_complexity": "Exact target distribution match",
                "contract_class": "APPLICATION",
                "verified": True
            }
        ]

    def get_all(self) -> List[Dict[str, Any]]:
        return self._entries
