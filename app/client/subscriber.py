import argparse
import asyncio
import json
import os
import time
import websockets

def now_ms():
    return int(time.time() * 1000)

async def run(client_id: str, url: str, log_dir: str):
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{client_id}.jsonl")

    async with websockets.connect(f"{url}?client_id={client_id}") as ws:
        print(f"[{client_id}] connected")

        async for msg in ws:
            received_at = now_ms()
            try:
                event = json.loads(msg)
                published_at = event.get("published_at_ms")
            except Exception:
                event = {"raw": msg}
                published_at = None

            latency = received_at - published_at if published_at else None

            print(f"[{client_id}] seq={event.get('sequence')} latency_ms={latency}")

            record = {
                "client_id": client_id,
                "event_id": event.get("event_id"),
                "sequence": event.get("sequence"),
                "published_at_ms": published_at,
                "received_at_ms": received_at,
                "latency_ms": latency,
            }

            with open(log_path, "a") as f:
                f.write(json.dumps(record) + "\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--url", default="ws://localhost:8000/ws")
    parser.add_argument("--log-dir", default="logs")
    args = parser.parse_args()

    asyncio.run(run(args.id, args.url, args.log_dir))

if __name__ == "__main__":
    main()
