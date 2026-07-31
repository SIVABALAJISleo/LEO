# Fetch Kimi model weights from GitHub Releases (bypassing LFS)

Write-Host "Downloading Kimi-k3 weights from GitHub Releases..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path models | Out-Null

Invoke-WebRequest -Uri "https://github.com/SIVABALAJISleo/LEO/releases/download/v1.0-weights/kimi-k3.gguf" -OutFile "models\kimi-k3.gguf"

Write-Host "Download complete! Weights saved to models\kimi-k3.gguf" -ForegroundColor Green
