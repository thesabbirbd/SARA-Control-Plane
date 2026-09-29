#!/usr/bin/env bash
set -e

echo "SARA Control Plane Installer"
echo "----------------------------"

if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required."
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "Git is required."
    exit 1
fi

echo "✓ Dependencies verified."

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Installing requirements..."
.venv/bin/pip install -r requirements.txt --quiet

echo "Preparing configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from example. Please edit it with your Telegram token."
fi

echo "Preparing user directories..."
mkdir -p ~/.config/sara
mkdir -p logs

echo "Setup complete! Run SARA with:"
echo "./start.sh"
