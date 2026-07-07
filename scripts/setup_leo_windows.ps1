# LEO AI — One-shot Windows benchmark setup (i5-12450H / UHD 48EU target)
# Run in PowerShell from the repo root:  .\scripts\setup_leo_windows.ps1
$ErrorActionPreference = "Stop"

Write-Host "=== LEO Layer 1 Benchmark Setup ===" -ForegroundColor Cyan

# 1) Python env
if (-not (Test-Path ".leoenv")) {
    python -m venv .leoenv
}
.\.leoenv\Scripts\Activate.ps1
python -m pip install --upgrade pip

# 2) Core deps + OpenVINO (this is what talks to the UHD iGPU on Windows)
pip install openvino openvino-genai numpy psutil
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers optimum[openvino] peft accelerate

# 3) Confirm the iGPU is visible
python -c "import openvino as ov; core = ov.Core(); print('DEVICES:', core.available_devices); [print(d, '->', core.get_property(d, 'FULL_DEVICE_NAME')) for d in core.available_devices]"

# Expected output MUST include:  GPU -> Intel(R) UHD Graphics ...
# If GPU is missing: update the Intel graphics driver from intel.com/download-center, reboot, rerun.

# 4) Run the real Layer 1 benchmark
$env:PYTHONPATH = (Get-Location).Path
python backend\benchmarks\layer1_silicon_bench.py --json-out backend\benchmarks\layer1_measured.json | Tee-Object -FilePath backend\benchmarks\layer1_MEASURED_i5-12450H.log

Write-Host "=== DONE — commit backend/benchmarks/layer1_MEASURED_i5-12450H.log ===" -ForegroundColor Green
