#!/usr/bin/env bash
# fetch_bitnet.sh
# Automates cloning and building microsoft/BitNet for Unix/macOS environments.
set -e

echo "=== Fetching and Building bitnet.cpp ==="

BUILD_DIR="build_bitnet"
if [ -d "$BUILD_DIR" ]; then
    rm -rf "$BUILD_DIR"
fi

git clone --recursive https://github.com/microsoft/BitNet.git "$BUILD_DIR"

cd "$BUILD_DIR"
python3 setup_env.py --hf-repo microsoft/BitNet-b1.58-2B-4T-gguf -q i2_s

BIN_SOURCE="build/bin/llama-cli"
BIN_DEST="../backend/inference/bin/bitnet-cli"

if [ -f "$BIN_SOURCE" ]; then
    cp "$BIN_SOURCE" "$BIN_DEST"
    echo "Success! bitnet-cli has been built and placed at $BIN_DEST"
else
    echo "Compilation finished, but llama-cli was not found. Please compile manually."
fi
