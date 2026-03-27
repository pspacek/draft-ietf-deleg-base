#!/usr/bin/bash
set -o nounset -o errexit

echo '=== KNOT ==='
dig -r @127.0.0.1 -p 5375 "$@"
echo '=== BIND ==='
dig -r @127.0.0.1 -p 5366 "$@"
