#!/bin/bash
# Auto-format all Python files in the project

set -e

cd "$(dirname "$0")/.."

echo "=== Formatting Code ==="
uv run black backend/ main.py
echo ""
echo "Done."
