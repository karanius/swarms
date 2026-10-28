#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

# Preserve the original one-script commands.
case "${1:-}" in
    --status) shift; set -- status "$@" ;;
    --no-browser) shift; set -- login --no-browser "$@" ;;
    --serve) shift; set -- serve "$@" ;;
    --configure) shift; set -- config set "$@" ;;
    --show-config) shift; set -- config show "$@" ;;
    --check-update) shift; set -- update "$@" ;;
esac

if [[ -z "${CARGO_TARGET_DIR:-}" ]]; then
    : "${HOME:?HOME must be set to store build artifacts outside this project}"
    export CARGO_TARGET_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/codex-authentication/target"
fi

if command -v rustup >/dev/null 2>&1; then
    if ! rustup which rustc --toolchain 1.99.1 >/dev/null 2>&1; then
        rustup toolchain install 1.99.1 --profile minimal
    fi
    export RUSTC="$(rustup which rustc --toolchain 1.99.1)"
    exec rustup run 1.99.1 cargo run --locked --quiet --bin api-proxy -- "$@"
fi

if command -v cargo >/dev/null 2>&1; then
    exec cargo run --locked --quiet --bin api-proxy -- "$@"
fi

echo "Rust is required. Install rustup, then run this script again." >&2
exit 1
