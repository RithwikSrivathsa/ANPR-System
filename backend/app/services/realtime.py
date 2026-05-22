import asyncio
import json
from collections.abc import AsyncIterator

import redis.asyncio as redis
from fastapi import WebSocket

from app.core.logging import get_logger

logger = get_logger(__name__)


class RealtimeBroker:
    def __init__(self, redis_url: str) -> None:
        self.redis_url = redis_url
        self.redis: redis.Redis | None = None
        self.clients: set[WebSocket] = set()
        self.channel = "anpr.events"

    async def connect(self) -> None:
        self.redis = redis.from_url(self.redis_url, decode_responses=True)
        try:
            await self.redis.ping()
        except Exception as exc:
            logger.warning("Redis unavailable, websocket local broadcast still works: %s", exc)

    async def close(self) -> None:
        if self.redis:
            await self.redis.close()

    async def publish(self, event: dict) -> None:
        message = json.dumps(event, default=str)
        if self.redis:
            try:
                await self.redis.publish(self.channel, message)
            except Exception as exc:
                logger.warning("Redis publish failed: %s", exc)
        await self.broadcast(message)

    async def broadcast(self, message: str) -> None:
        stale: list[WebSocket] = []
        for client in self.clients:
            try:
                await client.send_text(message)
            except Exception:
                stale.append(client)
        for client in stale:
            self.clients.discard(client)

    async def register(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.clients.add(websocket)

    def unregister(self, websocket: WebSocket) -> None:
        self.clients.discard(websocket)

    async def redis_events(self) -> AsyncIterator[str]:
        if not self.redis:
            return
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(self.channel)
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield message["data"]
        finally:
            await pubsub.unsubscribe(self.channel)
            await pubsub.close()


class ConnectionHeartbeat:
    def __init__(self, websocket: WebSocket) -> None:
        self.websocket = websocket

    async def keepalive(self) -> None:
        while True:
            await asyncio.sleep(25)
            await self.websocket.send_json({"type": "heartbeat"})
