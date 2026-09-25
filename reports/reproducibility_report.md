# Reproducibility Manifest & Environment Verification Report

## 1. Host Execution Environment
- **Operating System:** Windows-11-10.0.26100-SP0
- **Python Version:** 3.13.5
- **CPU:** 13th Gen Intel(R) Core(TM) i5-13420H
- **System RAM (GB):** 15.7
- **iGPU Info:** Intel(R) UHD Graphics
- **Git Commit / Version:** f046e1bf8998b88e7833f8951a155b99346cedaf

## 2. Software Stack Versions
- **NumPy:** 2.3.2
- **Platform Architecture:** AMD64

## 3. Execution Commands to Reproduce
To re-run the entire benchmark suite and verify output hashes independently:
```bash
# Run discovery CLI in research mode
python -m hyper.cli discover exp_a_chained_gemm --research

# Run audit falsification
python -m hyper.cli audit exp_e_cryptographic_hash

# Run complete adversarial and benchmark suite
python -m pytest tests/test_cir.py tests/test_contract.py tests/test_search_and_verifier.py tests/test_pathway_api.py -v
```

## 4. Verification Checksums
- **Exp_A (Matrix Computation (Chained GEMM)):** Candidate Hash `92be735f8e55fb83bf7a83047c92b558ec174a9f3763fb4c9db021351a70daef` | Reference Hash `1f814ffe47068da87d23c07634956437948749e2e2f967ade2a5a0a4bf1906ab`
- **Exp_B (Convolution (2D Conv + ReLU Fusion)):** Candidate Hash `0d4ca5f9a32c0f22c0d8a2f426f2aef154905c9568cced106cdc072c49dbe698` | Reference Hash `0d4ca5f9a32c0f22c0d8a2f426f2aef154905c9568cced106cdc072c49dbe698`
- **Exp_C (FFT / Spectral Decomposition):** Candidate Hash `4b1b63dfa8ed2690ae1b4a2bf5ddfafe52056947edfc7f430063986a113a28a5` | Reference Hash `4b1b63dfa8ed2690ae1b4a2bf5ddfafe52056947edfc7f430063986a113a28a5`
- **Exp_D (Graph Computation (Sparse Adjacency)):** Candidate Hash `12d5b838971b3dfce06eef3a500e9810e157b55a448be1ac4c894891d2cbc193` | Reference Hash `12d5b838971b3dfce06eef3a500e9810e157b55a448be1ac4c894891d2cbc193`
- **Exp_E (Cryptographic Hash (SHA-256)):** Candidate Hash `ce6b480c620cd365f96caa49ecce626589514642d3ba27bfa9bdaacf2fd7462c` | Reference Hash `ce6b480c620cd365f96caa49ecce626589514642d3ba27bfa9bdaacf2fd7462c`
- **Exp_F (Scientific Numerical ODE):** Candidate Hash `e09a08b9162ee493f112e1c78e9107963c3a1d6745d82ba26880ea5e1be62a34` | Reference Hash `e09a08b9162ee493f112e1c78e9107963c3a1d6745d82ba26880ea5e1be62a34`
- **Exp_G (ML Inference (Projection + Dead Code)):** Candidate Hash `9b474b4e8acf780d59526c8d6649417b0166bacc1f6a5f1db8d3981113687daa` | Reference Hash `9b474b4e8acf780d59526c8d6649417b0166bacc1f6a5f1db8d3981113687daa`
- **Exp_H (Irregular Memory Access (Gather)):** Candidate Hash `a7b8a7a0d40937aec87be9f38f2702989ce81d14abd63df05ddb31c1246685c3` | Reference Hash `a7b8a7a0d40937aec87be9f38f2702989ce81d14abd63df05ddb31c1246685c3`
- **Exp_I (Memory-Bound (STREAM Vector Triad)):** Candidate Hash `193618d45e79132d11b507eb30fe32daac555adbad40d1011f6f41de50efa74f` | Reference Hash `193618d45e79132d11b507eb30fe32daac555adbad40d1011f6f41de50efa74f`
- **Exp_J (Compute-Bound (Polynomial Horner)):** Candidate Hash `7319bbaf7519dda57a829acbf3ab6cf73b7199b597b8cbe75067f10f48a61280` | Reference Hash `7319bbaf7519dda57a829acbf3ab6cf73b7199b597b8cbe75067f10f48a61280`