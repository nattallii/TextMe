import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.models.chat import Chat
from src.schemas.message import MessageCreate
from src.ws.connection_manager import manager
from src.ws.schemas import (
    WebSocketMessageType,
    TypingData,
    MessageReadData,
    NewMessageData,
    UserJoinedData,
    UserLeftData,
)
from src.ws.auth import get_user_from_ws
from src.redis.client import redis_client
from src.redis.service import RedisService
from src.services.chat import ChatService

chat_service = ChatService()
redis_service = RedisService(redis_client)

router = APIRouter()

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.models.chat import Chat
from src.services.chat import ChatService
from src.ws.auth import get_user_from_ws
from src.ws.connection_manager import manager
from src.ws.schemas import (
    WebSocketMessageType,
    TypingData,
    MessageReadData,
    UserJoinedData,
    UserLeftData,
)
from src.redis.client import redis_client
from src.redis.service import RedisService

router = APIRouter()

chat_service = ChatService()
redis_service = RedisService(redis_client)


@router.websocket("/ws/chat/{chat_id}")
async def ws_chat(
    ws: WebSocket,
    chat_id: str,
):
    await ws.accept()

    try:
        user_id = await get_user_from_ws(ws)

    except Exception:
        await ws.close(code=1008)
        return

    chat = await Chat.get(chat_id)

    if not chat:
        await ws.close(code=1008)
        return

    if user_id not in chat.members:
        await ws.close(code=1008)
        return

    await manager.connect(
        ws,
        chat_id,
        user_id,
    )

    await redis_service.set_online(user_id)

    await manager.send_user_joined(
        UserJoinedData(
            chat_id=chat_id,
            user_id=user_id,
        )
    )

    try:
        while True:

            raw = await ws.receive_text()

            try:
                payload = json.loads(raw)

            except json.JSONDecodeError:

                await manager.send_error(
                    chat_id,
                    code="invalid_json",
                    text="Invalid JSON",
                )

                continue

            msg_type = payload.get("type")
            data = payload.get("data", {})

            # =========================
            # TYPING
            # =========================

            if msg_type == WebSocketMessageType.TYPING:

                is_typing = data.get(
                    "is_typing",
                    False,
                )

                if is_typing:

                    if not await redis_service.is_typing(
                        chat_id,
                        user_id,
                    ):
                        await redis_service.set_typing(
                            chat_id,
                            user_id,
                        )

                await manager.send_typing(
                    TypingData(
                        chat_id=chat_id,
                        user_id=user_id,
                        is_typing=is_typing,
                    )
                )

            # =========================
            # MESSAGE READ
            # =========================

            elif msg_type == WebSocketMessageType.MESSAGE_READ:

                message_id = data.get("message_id")

                if not message_id:
                    continue

                await chat_service.mark_as_read(
                    message_id=message_id,
                    user_id=user_id,
                )

                await redis_service.reset_unread(
                    user_id,
                    chat_id,
                )

                await manager.send_read(
                    MessageReadData(
                        chat_id=chat_id,
                        message_id=message_id,
                        user_id=user_id,
                    )
                )

            # =========================
            # UNKNOWN EVENT
            # =========================

            else:

                await manager.send_error(
                    chat_id,
                    code="unknown_type",
                    text="Unknown websocket event type",
                )

    except WebSocketDisconnect:

        await manager.disconnect(
            ws,
            chat_id,
            user_id,
        )

        await redis_service.set_offline(user_id)

        await manager.send_user_left(
            UserLeftData(
                chat_id=chat_id,
                user_id=user_id,
            )
        )