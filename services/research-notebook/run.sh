#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
if [ ! -x services/research-notebook/.venv/bin/python ]; then
  uv venv --python 3.12 services/research-notebook/.venv
fi
if ! services/research-notebook/.venv/bin/python -c "import notebook, ipykernel" >/dev/null 2>&1; then
  uv pip install --python services/research-notebook/.venv/bin/python -r services/research-notebook/requirements.lock
fi
exec services/research-notebook/.venv/bin/python services/research-notebook/start.py
