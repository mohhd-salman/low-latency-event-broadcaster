#!/usr/bin/env bash
set -euo pipefail

if [ ! -d ".pids" ]; then
  echo "No .pids directory found."
  exit 0
fi

echo "Stopping subscribers..."
for f in .pids/*.pid; do
  [ -e "$f" ] || continue
  pid="$(cat "$f")"
  kill "$pid" 2>/dev/null || true
done

rm -rf .pids
echo "Stopped."
