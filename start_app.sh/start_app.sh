#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.11 or newer was not found."
  echo "Install Python and run this file again."
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "First launch: creating the local environment..."
  python3 -m venv .venv
  echo "First launch: installing dependencies..."
  .venv/bin/python -m pip install -r requirements.txt
fi

(sleep 2; if command -v xdg-open >/dev/null 2>&1; then xdg-open http://127.0.0.1:8000; elif command -v open >/dev/null 2>&1; then open http://127.0.0.1:8000; fi) &
exec .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
