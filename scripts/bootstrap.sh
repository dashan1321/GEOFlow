#!/usr/bin/env bash
set -euo pipefail

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python3 -m pip install -r requirements.txt

if [ ! -f ".env" ]; then
  cp .env.example .env
fi

echo "Bootstrap complete."
echo "Next steps:"
echo "  1. source .venv/bin/activate"
echo "  2. edit .env"
echo "  3. python run.py"
