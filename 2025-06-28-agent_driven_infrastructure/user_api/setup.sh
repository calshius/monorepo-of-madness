#!/bin/bash
set -e

# Upgrade pip
pip install --upgrade pip

if ! command -v pipx &> /dev/null; then
    pip install pipx
    pipx ensurepath
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install uv using pipx if not already installed
if ! command -v uv &> /dev/null; then
    pipx install uv
fi

# Create a virtual environment in the current directory
if [ ! -d ".venv" ]; then
    uv venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install the package in editable mode using uv
uv pip install -e .