import redis.asyncio as redis


class RedisService:
    def __init__(self, client: redis.Redis):
        self.client = client


    async def publish(self, channel: str, message: dict):
        import json
        await self.client.publish(channel, json.dumps(message))

    async def subscribe(self, channel: str):
        pubsub = self.client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    async def set_online(self, user_id: int):
        await self.client.set(f"user:{user_id}:online", "1")

    async def set_offline(self, user_id: int):
        await self.client.delete(f"user:{user_id}:online")

    async def is_online(self, user_id: int) -> bool:
        return await self.client.exists(f"user:{user_id}:online") == 1

    async def set_typing(self, chat_id: str, user_id: int):
        await self.client.set(
            f"typing:{chat_id}:{user_id}",
            "1",
            ex=5
        )

    async def is_typing(self, chat_id: str, user_id: int) -> bool:
        return await self.client.exists(f"typing:{chat_id}:{user_id}") == 1

    async def increment_unread(self, user_id: int, chat_id: str):
        key = f"unread:{user_id}:{chat_id}"
        await self.client.incr(key)

    async def reset_unread(self, user_id: int, chat_id: str):
        await self.client.delete(f"unread:{user_id}:{chat_id}")

    async def get_unread(self, user_id: int, chat_id: str) -> int:
        value = await self.client.get(f"unread:{user_id}:{chat_id}")
        return int(value) if value else 0

