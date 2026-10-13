#!/bin/zsh
set -eu
service_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
if launchctl print "gui/$(id -u)/local.swarms.log-pipeline" >/dev/null 2>&1; then
  exec launchctl kickstart "gui/$(id -u)/local.swarms.log-pipeline"
fi
cd "$service_dir/.."
exec "$service_dir/swarm-runtime-venv/bin/python" -m uvicorn services.log_pipeline:app --host 127.0.0.1 --port 52418
