#!/bin/bash
# Fetch Kimi model weights from GitHub Releases (bypassing LFS)

echo "Downloading Kimi-k3 weights from GitHub Releases..."
mkdir -p models

curl -L -o models/kimi-k3.gguf \
  https://github.com/SIVABALAJISleo/LEO/releases/download/v1.0-weights/kimi-k3.gguf

echo "Download complete! Weights saved to models/kimi-k3.gguf"
