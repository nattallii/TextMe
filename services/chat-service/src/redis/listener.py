import json
from src.redis.service import RedisService
from src.redis.client import redis_client
from src.ws.connection_manager import manager

redis_service = RedisService(redis_client)

async def redis_listener():
    pubsub = await redis_service.subscribe("chat_events")

    async for msg in pubsub.listen():
        if msg["type"] != "message":
            continue

        data = msg["data"]

        if isinstance(data, bytes):
            data = data.decode()

        data = json.loads(data)

        if data["type"] == "new_message":
            await manager.broadcast(
                data["chat_id"],
                data["data"]
            )