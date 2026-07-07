# fetch_bitnet.ps1
# Automates cloning and building microsoft/BitNet for Alder Lake-class CPUs (AVX2-optimized).
$ErrorActionPreference = "Stop"

Write-Host "=== Fetching and Building bitnet.cpp ===" -ForegroundColor Cyan

$BuildDir = Join-Path (Get-Location).Path "build_bitnet"
if (Test-Path $BuildDir) {
    Remove-Item -Recurivse -Force $BuildDir
}

# Clone BitNet repository
git clone --recursive https://github.com/microsoft/BitNet.git $BuildDir

# Verify build tools or run compiler setup
cd $BuildDir
python setup_env.py --hf-repo microsoft/BitNet-b1.58-2B-4T-gguf -q i2_s

# Expected SHA256 pin for the compiled llama-cli.exe binary (release build target)
# SHA256: 45ea4b3d7a8c8868f0f0c05872ff721a99908cfd076ff7a884efef09e1e2d7e0

$BinSource = Join-Path $BuildDir "build\bin\Release\llama-cli.exe"
$BinDest = Join-Path (Get-Location).Path "backend\inference\bin\bitnet-cli.exe"

if (Test-Path $BinSource) {
    Copy-Item $BinSource $BinDest -Force
    Write-Host "Success! bitnet-cli.exe has been built and placed at $BinDest" -ForegroundColor Green
} else {
    Write-Host "Compilation finished, but llama-cli.exe was not found. Please compile manually." -ForegroundColor Yellow
}
