#!/bin/bash

# This script starts the Ollama server and ensures the Qwen 2.5‑Coder 14B model is
# available. Run this after executing install_backend.sh. It runs the Ollama
# daemon in the foreground; stop it with Ctrl+C. See docs/LOCAL_AGENT.md for more
# details.

set -e

MODEL="qwen2.5-coder:14b"

echo "Starting Ollama server..."
# Start the Ollama server. This keeps running until you stop it manually.
ollama serve &
SERVER_PID=$!

echo "Waiting for Ollama server to initialize..."
sleep 5

echo "Ensuring model $MODEL is pulled..."
# Pull the model if it hasn't been downloaded already.
ollama pull "$MODEL" || true

echo "Ollama server started with PID $SERVER_PID."
echo "You can now interact with the model via the agent or by sending requests to http://localhost:11434/."
wait $SERVER_PID