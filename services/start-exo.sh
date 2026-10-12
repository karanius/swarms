#!/bin/zsh
set -eu
service_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
export EXO_HOME="$service_dir/exo-runtime"
cd "$service_dir/exo"
exec uv run --no-sync exo --api-port 52416 --namespace swarms-canvas --offline "$@"
