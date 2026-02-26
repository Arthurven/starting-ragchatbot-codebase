#!/bin/bash
# Run code quality checks for the project

set -e

cd "$(dirname "$0")/.."

echo "=== Code Quality Checks ==="
echo ""

# Formatting check
echo "--- Black (formatting) ---"
if uv run black --check backend/ main.py 2>&1; then
    echo "All files formatted correctly."
else
    echo ""
    echo "Run 'uv run black backend/ main.py' to fix formatting."
    exit 1
fi

echo ""
echo "All checks passed."
