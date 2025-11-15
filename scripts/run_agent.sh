#!/bin/bash

# Script to start the local agent's API server. It assumes that the Ollama
# backend is already running (see run_backend.sh). The server uses uvicorn to
# serve FastAPI. You can pass additional arguments to uvicorn by editing this
# file.

set -e

# Activate python virtual environment if needed. Here we assume python3 is
# available in PATH. You may customise this script to suit your environment.

PORT=${PORT:-8000}

echo "Starting agent server on port $PORT..."
python3 -m uvicorn server.api:app --host 0.0.0.0 --port "$PORT"