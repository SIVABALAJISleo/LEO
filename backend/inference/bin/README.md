# LEO AI Ternary Engine Binaries

Place the built Microsoft `bitnet.cpp` binary (e.g., `llama-cli.exe` or `bitnet-cli`) inside this directory.

## Build Instructions (Windows)
1. Clone Microsoft BitNet:
   ```powershell
   git clone --recursive https://github.com/microsoft/BitNet.git C:\bitnet
   cd C:\bitnet
   ```
2. Build via the setup script:
   ```powershell
   python setup_env.py --hf-repo microsoft/BitNet-b1.58-2B-4T-gguf -q i2_s
   ```
3. Copy `build\bin\Release\llama-cli.exe` to this directory and rename/symlink it to `bitnet-cli` or leave it as `llama-cli.exe`.

## Expected Model Paths
- Model GGUF files should be placed at `models/bitnet/` or configured in your environment under `LEO_BITNET_MODEL_PATH`.
