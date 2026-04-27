import json
import aio_pika
from sqlalchemy import select

from src.messaging import rabbitmq
from src.db.session import engine
from src.models.models import UserProfile
from src.db.session import AsyncSessionLocal


EXCHANGE_NAME = 'exchange'
QUEUE_NAME = "profile.user.registered"
ROUTING_KEY = 'user.registered'


async def process_user_register(message: aio_pika.IncomingMessage) -> None:
    async with message.process():
        payload = json.loads(message.body.decode())

        user_id = payload['user_id']
        username = payload['username']
        phone = payload['phone']
        email = payload['email']

        async with AsyncSessionLocal() as session:
            existing_profile = await session.scalar(
                select(UserProfile).where(UserProfile.user_id == user_id)
            )

            if existing_profile:
                return

            profile = UserProfile(
                user_id=user_id,
                username=username,
                phone=phone,
                email=email,
                bio='',
            )

            session.add(profile)
            await session.commit()


async def start_consumer() -> None:
    if rabbitmq.channel is None:
        raise RuntimeError('channel is not initialized')

    exchange = await rabbitmq.channel.declare_exchange(
        EXCHANGE_NAME,
        aio_pika.ExchangeType.TOPIC,
        durable=True
    )

    queue = await rabbitmq.channel.declare_queue(
        QUEUE_NAME,
        durable=True
    )

    await queue.bind(exchange, routing_key=ROUTING_KEY)
    await queue.consume(process_user_register)