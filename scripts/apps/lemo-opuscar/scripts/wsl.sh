#!/usr/bin/env bash
# Windows bridge for Lemo-Opuscar: the library and its tools live inside WSL (native Windows is unsupported).
#   bash wsl.sh setup [deps [voice] [music] | demo <slug>]   run setup.sh inside WSL (same arguments)
#   bash wsl.sh run '<command>'                               run a shell command inside WSL, starting in $LIB
#   bash wsl.sh path '<Windows path>'                         print its WSL form (D:\a b -> /mnt/d/a b)
# LEMO_WSL_DISTRO / LEMO_WSL_LIB override the distro (Ubuntu-24.04) and library path (/root/lemo-opuscar).
set -euo pipefail
export MSYS_NO_PATHCONV=1   # stop Git Bash from rewriting /root/... into C:/Program Files/Git/root/...
DISTRO="${LEMO_WSL_DISTRO:-Ubuntu-24.04}"
LIB="${LEMO_WSL_LIB:-/root/lemo-opuscar}"
HERE_WIN="$(cd "$(dirname "$0")" && pwd -W)"

to_wsl() { wsl.exe -d "$DISTRO" -- wslpath -a "$1" | tr -d '\r'; }

case "${1:-}" in
  setup) shift; exec wsl.exe -d "$DISTRO" --cd /root -- env LEMO_OPUSCAR_HOME="$LIB" sh "$(to_wsl "$HERE_WIN/setup.sh")" "$@" ;;
  run)   [ -n "${2:-}" ] || { echo "usage: bash wsl.sh run '<command>'" >&2; exit 2; }
         exec wsl.exe -d "$DISTRO" --cd "$LIB" -- bash -lc "$2" ;;
  path)  [ -n "${2:-}" ] || { echo "usage: bash wsl.sh path '<Windows path>'" >&2; exit 2; }
         to_wsl "$2" ;;
  *)     sed -n '2,6p' "$0"; exit 2 ;;
esac
