import os, asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import redis.asyncio as redis
from .stats import StatsStore
from .redis_subscriber import RedisSubscriber
from .ws_manager import WSManager

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_CHANNEL = os.getenv("REDIS_CHANNEL", "events.critical")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

stats_store = StatsStore()
ws_manager = WSManager()
subscriber = RedisSubscriber(redis_client, REDIS_CHANNEL, stats_store, ws_manager)
subscriber_task = None

@app.on_event("startup")
async def startup():
    global subscriber_task
    subscriber_task = asyncio.create_task(subscriber.run())

@app.on_event("shutdown")
async def shutdown():
    subscriber.stop()
    if subscriber_task:
        subscriber_task.cancel()
    await redis_client.close()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/stats")
async def stats():
    await stats_store.set_connected_clients(await ws_manager.connected_count())
    return await stats_store.snapshot()

@app.websocket("/ws")
async def ws(websocket: WebSocket):
    client_id = websocket.query_params.get("client_id")
    if not client_id:
        await websocket.close(code=1008)
        return

    await ws_manager.register(client_id, websocket)
    await stats_store.set_connected_clients(await ws_manager.connected_count())

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.unregister(client_id)
        await stats_store.set_connected_clients(await ws_manager.connected_count())
