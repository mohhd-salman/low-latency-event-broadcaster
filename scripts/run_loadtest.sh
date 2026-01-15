#!/usr/bin/env bash
set -euo pipefail

CLIENTS="${CLIENTS:-50}"
EVENTS="${EVENTS:-50}"
URL="${URL:-ws://localhost:8000/ws}"
LOG_DIR="${LOG_DIR:-logs}"

# Ensure venv is active
python -c "import websockets" >/dev/null 2>&1 || {
  echo "ERROR: Activate your venv first: source .venv/bin/activate"
  exit 1
}

# Stop any running clients
if [ -f scripts/stop_clients.sh ]; then
  scripts/stop_clients.sh || true
fi

# Clear logs
mkdir -p "$LOG_DIR"
rm -f "$LOG_DIR"/svc-*.jsonl "$LOG_DIR"/svc-*.out || true

# Start clients
echo "Starting $CLIENTS subscribers..."
CLIENTS="$CLIENTS" URL="$URL" LOG_DIR="$LOG_DIR" scripts/run_clients.sh "$CLIENTS"

# Wait for connections to stabilize
sleep 2

# Publish events
echo "Publishing $EVENTS events..."
REDIS_HOST=localhost python -m app.publisher.publish \
  --type SERVER_DOWN \
  --source server-a \
  --count "$EVENTS" \
  --interval-ms 0 >/dev/null

# Wait for delivery + logging
sleep 2

# Report
echo ""
python -m app.loadtest.report --log-dir "$LOG_DIR" --clients "$CLIENTS" --events "$EVENTS"
echo ""

# Cleanup
scripts/stop_clients.sh || true
