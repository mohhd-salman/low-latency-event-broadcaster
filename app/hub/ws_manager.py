import asyncio
from dataclasses import dataclass
from typing import Dict
from fastapi import WebSocket

@dataclass
class ClientConn:
    client_id: str
    websocket: WebSocket
    queue: asyncio.Queue
    task: asyncio.Task

class WSManager:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._clients: Dict[str, ClientConn] = {}

    async def register(self, client_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        queue: asyncio.Queue = asyncio.Queue()
        task = asyncio.create_task(self._sender_loop(client_id, websocket, queue))
        async with self._lock:
            self._clients[client_id] = ClientConn(client_id, websocket, queue, task)

    async def unregister(self, client_id: str) -> None:
        async with self._lock:
            conn = self._clients.pop(client_id, None)
        if conn:
            conn.task.cancel()

    async def connected_count(self) -> int:
        async with self._lock:
            return len(self._clients)

    async def broadcast(self, message: str) -> None:
        async with self._lock:
            conns = list(self._clients.values())
        for conn in conns:
            await conn.queue.put(message)

    async def _sender_loop(self, client_id: str, websocket: WebSocket, queue: asyncio.Queue):
        try:
            while True:
                msg = await queue.get()
                await websocket.send_text(msg)
        except Exception:
            pass
