#!/bin/zsh
set -eu
service_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
cd "$service_dir/.."
exec "$service_dir/swarm-runtime-venv/bin/python" -m uvicorn services.swarm_loop:app --host 127.0.0.1 --port 52417
