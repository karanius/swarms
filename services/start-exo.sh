#!/bin/zsh
set -eu
service_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
export EXO_HOME="$service_dir/exo-runtime"
macmon_helper="/Applications/EXO.app/Contents/Resources/exo/_internal/macmon"
if [[ -z "${EXO_MACMON_PATH:-}" && -x "$macmon_helper" ]]; then
  export EXO_MACMON_PATH="$macmon_helper"
fi
cd "$service_dir/exo"
# Match the installed peer's libp2p protocol; the current source uses Zenoh.
export EXO_LIBP2P_NAMESPACE="${EXO_LIBP2P_NAMESPACE:-1.0.71}"
export EXO_MODELS_READ_ONLY_DIRS="${EXO_MODELS_READ_ONLY_DIRS:-$HOME/.exo/models}"
"$service_dir/exo/.venv/bin/python" "$service_dir/discover-exo-peers.py" &
exec /Applications/EXO.app/Contents/Resources/exo/exo --api-port 52416 --offline --no-fast-synch "$@"
