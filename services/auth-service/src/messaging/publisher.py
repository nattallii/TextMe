import json
import aio_pika
from src.messaging import rabbitmq

EXCHANGE_NAME = 'exchange'

async def publish_user_register(user_id: int, phone: str, email: str, username: str) -> None:
    if rabbitmq.channel is None:
        raise RuntimeError('RabbitMQ channel is not initialized')

    exchange = await rabbitmq.channel.declare_exchange(
        EXCHANGE_NAME,
        aio_pika.ExchangeType.TOPIC,
        durable=True
    )

    message = {
        'user_id': user_id,
        'username': username,
        'email': email,
        'phone': phone,
    }

    await exchange.publish(
        aio_pika.Message(body=json.dumps(message).encode(),
        content_type = 'application/json',
        delivery_mode = aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key='user.registered',

    )
