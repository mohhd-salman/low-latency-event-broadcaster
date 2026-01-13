import json
import os
import glob
from typing import List


def percentile(sorted_vals: List[int], p: float) -> int:
    if not sorted_vals:
        return 0
    k = (len(sorted_vals) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    return int(sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f))


def main(log_dir: str, clients: int, events: int) -> None:
    paths = sorted(glob.glob(os.path.join(log_dir, "svc-*.jsonl")))
    latencies = []
    received = 0

    for p in paths:
        with open(p, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    if rec.get("latency_ms") is not None:
                        latencies.append(int(rec["latency_ms"]))
                    received += 1
                except Exception:
                    continue

    expected = clients * events
    dropped = max(expected - received, 0)

    latencies.sort()
    p50 = percentile(latencies, 0.50)
    p95 = percentile(latencies, 0.95)
    p99 = percentile(latencies, 0.99)
    mx = latencies[-1] if latencies else 0

    print(f"Clients: {clients}")
    print(f"Events: {events}")
    print(f"Expected deliveries: {expected}")
    print(f"Received deliveries: {received}")
    print(f"Dropped deliveries: {dropped}\n")

    print("Latency (ms):")
    print(f"p50: {p50}")
    print(f"p95: {p95}")
    print(f"p99: {p99}")
    print(f"max: {mx}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--log-dir", default="logs")
    parser.add_argument("--clients", type=int, default=50)
    parser.add_argument("--events", type=int, default=50)
    args = parser.parse_args()

    main(args.log_dir, args.clients, args.events)
