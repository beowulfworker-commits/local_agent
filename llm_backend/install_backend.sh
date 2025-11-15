#!/bin/bash

# This script installs the Ollama runtime and downloads the Qwen 2.5‑Coder 14B model.
# It is intended to be run on a Linux/WSL system. It does not run automatically; you
# should execute it manually from the repository root. See docs/LOCAL_AGENT.md for
# usage instructions.

set -e

echo "Checking for Ollama..."
if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama not found. Installing Ollama via the official installation script..."
  # Install Ollama using the official install script. See the Ollama docs for details.
  # Source: https://ollama.com/download/linux
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "Ollama is already installed."
fi

echo "Pulling Qwen2.5‑Coder 14B model..."
# Download the model. This may take a while (~9 GB) depending on your internet connection.
ollama pull qwen2.5-coder:14b

echo "Installation complete. You can now run the backend using scripts/run_backend.sh."