#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
PYTHON="$ROOT/services/research-notebook/.venv/bin/python"
if [ ! -x "$PYTHON" ]; then
  echo "Research Python environment is missing; restore services/research-notebook first." >&2
  exit 1
fi
"$PYTHON" -c 'import requests, pysbd' || exit 1
cd "$ROOT"
exec "$PYTHON" services/speaker-studio/server.py
