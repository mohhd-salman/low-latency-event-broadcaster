import os, asyncio
from fastapi import FastAPI
import redis.asyncio as redis

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_CHANNEL = os.getenv("REDIS_CHANNEL", "events.critical")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


@app.get("/health")
async def health():
    return {"status": "ok"}

