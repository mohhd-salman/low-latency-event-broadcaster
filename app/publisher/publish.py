import argparse
import json
import os
import time
import uuid

import redis


def now_ms() -> int:
    return int(time.time() * 1000)


def build_event(event_type: str, source: str, sequence: int, message: str | None) -> dict:
    payload = {"message": message or f"{event_type} from {source}"}
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "source": source,
        "sequence": sequence,
        "published_at_ms": now_ms(),
        "payload": payload,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish events to Redis Pub/Sub")
    parser.add_argument("--type", required=True, help="Event type (e.g., SERVER_DOWN)")
    parser.add_argument("--source", required=True, help="Event source (e.g., server-a)")
    parser.add_argument("--count", type=int, default=1, help="Number of events to publish")
    parser.add_argument("--interval-ms", type=int, default=0, help="Delay between events (ms)")
    parser.add_argument("--message", default=None, help="Optional payload message")
    args = parser.parse_args()

    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    channel = os.getenv("REDIS_CHANNEL", "events.critical")

    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

    for seq in range(1, args.count + 1):
        event = build_event(args.type, args.source, seq, args.message)
        r.publish(channel, json.dumps(event))
        print(f"[publisher] published seq={seq} event_id={event['event_id']} to {channel}")

        if args.interval_ms > 0:
            time.sleep(args.interval_ms / 1000.0)


if __name__ == "__main__":
    main()
