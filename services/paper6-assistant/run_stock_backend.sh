#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
STOCK_ROOT="$PWD/services/paper6-assistant/.runtime/stock-builder"
mkdir -p "$STOCK_ROOT/fs"
export LANGFLOW_CONFIG_DIR="$STOCK_ROOT"
export LANGFLOW_DATABASE_URL="sqlite:///$STOCK_ROOT/langflow.db"
export LANGFLOW_FS_TOOL_BASE_DIR="$STOCK_ROOT/fs"
export LANGFLOW_AUTO_LOGIN=true LANGFLOW_DO_NOT_TRACK=true DO_NOT_TRACK=1
export OPENAI_API_KEY=local-proxy OPENAI_BASE_URL=http://127.0.0.1:8787/v1
exec /Users/x/projects/langflow/.venv/bin/python -m langflow run --host 127.0.0.1 --port 7861 --workers 1 --backend-only
