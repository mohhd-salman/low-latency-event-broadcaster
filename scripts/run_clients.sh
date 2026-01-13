#!/usr/bin/env bash
set -euo pipefail

N="${1:-50}"
URL="${URL:-ws://localhost:8000/ws}"
LOG_DIR="${LOG_DIR:-logs}"

mkdir -p "$LOG_DIR"
mkdir -p .pids

echo "Starting $N subscribers..."
for i in $(seq 1 "$N"); do
  cid="svc-$i"
  python -m app.client.subscriber --id "$cid" --url "$URL" --log-dir "$LOG_DIR" \
    > "$LOG_DIR/$cid.out" 2>&1 &
  echo $! > ".pids/$cid.pid"
done
