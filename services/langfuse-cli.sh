#!/bin/zsh
set -eu
service_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
set -a
source "$service_dir/langfuse/.env"
set +a
export LANGFUSE_BASE_URL="http://127.0.0.1:$LANGFUSE_PORT"
exec "$service_dir/langfuse/cli/node_modules/.bin/langfuse" --host "$LANGFUSE_BASE_URL" "$@"
