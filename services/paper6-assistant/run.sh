#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
exec /Users/x/projects/langflow/.venv/bin/python -m uvicorn server:app --app-dir services/paper6-assistant --host 127.0.0.1 --port 5192 --log-level warning
