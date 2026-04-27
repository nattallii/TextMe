import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel
from src.security.config import settings


connection: AbstractRobustConnection | None = None
channel: AbstractRobustChannel | None = None

async def connect_rabbitmq():
    global connection, channel
    print("Connecting to RabbitMQ...")

    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()
    print("rabbitMQ connected")

async def close_rabbitmq():
    global connection, channel
    if connection:
        await connection.close()