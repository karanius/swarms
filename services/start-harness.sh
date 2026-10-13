#!/bin/zsh
set -eu
service_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
export DSH_HOME="$service_dir/harness-runtime"
export DSH_TELEMETRY_DISABLED=1
cd "$service_dir/deepseek-harness"
exec pnpm dsh --profile web --host 127.0.0.1 --port 3080 --no-open "$@"
