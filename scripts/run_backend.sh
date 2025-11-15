#!/bin/bash

# Wrapper script that delegates to llm_backend/run_backend.sh. This exists for
# convenience so that all scripts can be run from the root of the repository.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

bash "$REPO_ROOT/llm_backend/run_backend.sh"