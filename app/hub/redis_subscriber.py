import asyncio
import json
import redis.asyncio as redis
from .stats import StatsStore
from .ws_manager import WSManager

class RedisSubscriber:
    def __init__(self, redis_client: redis.Redis, channel: str, stats: StatsStore, ws_manager: WSManager):
        self.redis_client = redis_client
        self.channel = channel
        self.stats = stats
        self.ws_manager = ws_manager
        self._stop_event = asyncio.Event()

    async def run(self) -> None:
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe(self.channel)

        try:
            while not self._stop_event.is_set():
                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if not msg:
                    continue

                data = msg.get("data")
                if isinstance(data, str):
                    try:
                        json.loads(data)
                    except Exception:
                        pass

                await self.stats.inc_events_received()
                await self.ws_manager.broadcast(data)

        finally:
            await pubsub.unsubscribe(self.channel)
            await pubsub.close()

    def stop(self):
        self._stop_event.set()
