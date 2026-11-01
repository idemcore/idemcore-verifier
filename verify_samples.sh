#!/bin/sh
# Same as `make verify`: recompute every published hash and re-check every pair.
cd "$(dirname "$0")" || exit 2
exec python3 -m idemcore_verify samples "$@"
