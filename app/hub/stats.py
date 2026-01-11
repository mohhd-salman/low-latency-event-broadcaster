import asyncio
from dataclasses import dataclass

@dataclass
class HubStats:
    events_received: int = 0
    connected_clients: int = 0

class StatsStore:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._stats = HubStats()

    async def inc_events_received(self) -> None:
        async with self._lock:
            self._stats.events_received += 1

    async def set_connected_clients(self, n: int) -> None:
        async with self._lock:
            self._stats.connected_clients = n

    async def snapshot(self) -> dict:
        async with self._lock:
            return {
                "connected_clients": self._stats.connected_clients,
                "events_received": self._stats.events_received,
            }
