#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-6006}"

exec python -m uvicorn server_app:app --host "${HOST}" --port "${PORT}"
