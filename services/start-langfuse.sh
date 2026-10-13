#!/bin/zsh
set -eu
service_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
exec docker compose --project-directory "$service_dir/langfuse" -f "$service_dir/langfuse/compose.yaml" up -d --no-build "$@"
