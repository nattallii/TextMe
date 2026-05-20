from fastapi import WebSocket
from collections import defaultdict

from src.ws.schemas import (
    WebSocketMessage,
    WebSocketMessageType,
    NewMessageData,
    TypingData,
    MessageReadData,
    UserJoinedData,
    UserLeftData,
    ErrorData,
)


class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, set[WebSocket]] = defaultdict(set)
        self.user_connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, ws: WebSocket, chat_id: str, user_id: int):
        self.connections[chat_id].add(ws)
        self.user_connections[user_id].add(ws)
        print(f"[connect] chat={chat_id} user={user_id} | user_connections keys={list(self.user_connections.keys())}")

    async def connect_user(self, ws: WebSocket, user_id: int):
        self.user_connections[user_id].add(ws)
        print(f"[connect_user] user={user_id} | all user_connections keys={list(self.user_connections.keys())}")

    async def disconnect(self, ws: WebSocket, chat_id: str, user_id: int):
        self.connections[chat_id].discard(ws)
        if not self.connections[chat_id]:
            del self.connections[chat_id]
        self.user_connections[user_id].discard(ws)
        if not self.user_connections[user_id]:
            del self.user_connections[user_id]
        print(f"[disconnect] chat={chat_id} user={user_id}")

    async def disconnect_user(self, ws: WebSocket, user_id: int):
        self.user_connections[user_id].discard(ws)
        if not self.user_connections[user_id]:
            del self.user_connections[user_id]
        print(f"[disconnect_user] user={user_id}")

    async def broadcast(self, chat_id: str, message):
        dead = []
        sockets = list(self.connections.get(chat_id, set()))
        print(f"[broadcast] chat={chat_id} sockets={len(sockets)}")
        for ws in sockets:
            try:
                payload = (
                    message if isinstance(message, dict)
                    else message.model_dump(mode="json")
                )
                await ws.send_json(payload)
            except Exception as e:
                print(f"[broadcast] ERROR: {e}")
                dead.append(ws)
        for ws in dead:
            self.connections[chat_id].discard(ws)
        if chat_id in self.connections and not self.connections[chat_id]:
            del self.connections[chat_id]

    async def send_to_user(self, user_id: int, payload: dict):
        sockets = list(self.user_connections.get(user_id, set()))
        print(f"[send_to_user] user={user_id} ({type(user_id).__name__}) | all_keys={list(self.user_connections.keys())} | found={len(sockets)}")
        dead = []
        for ws in sockets:
            try:
                await ws.send_json(payload)
            except Exception as e:
                print(f"[send_to_user] ERROR user={user_id}: {e}")
                dead.append(ws)
        for ws in dead:
            self.user_connections[user_id].discard(ws)
        if user_id in self.user_connections and not self.user_connections[user_id]:
            del self.user_connections[user_id]

    async def send_new_message(self, data: NewMessageData, member_ids: list[int]):
        print(f"[send_new_message] chat={data.chat_id} members={member_ids}")
        message = WebSocketMessage(
            type=WebSocketMessageType.NEW_MESSAGE,
            data=data.model_dump(mode="json"),
        )
        payload = message.model_dump(mode="json")
        await self.broadcast(data.chat_id, message)
        for user_id in member_ids:
            await self.send_to_user(user_id, payload)

    async def send_new_chat(self, chat):
        print(f"[send_new_chat] chat={chat.id} members={chat.members}")
        payload = {
            "type": "new_chat",
            "data": {
                "id": str(chat.id),
                "type": chat.type,
                "members": chat.members,
                "name": chat.name,
                "last_message": chat.last_message,
                "last_message_at": (
                    chat.last_message_at.isoformat() if chat.last_message_at else None
                ),
                "created_by": chat.created_by,
                "created_at": chat.created_at.isoformat(),
                "updated_at": (
                    chat.updated_at.isoformat() if chat.updated_at else None
                ),
                "is_deleted": chat.is_deleted,
                "unread_count": 0,
            },
        }
        for user_id in chat.members:
            await self.send_to_user(user_id, payload)

    async def send_typing(self, data: TypingData):
        message = WebSocketMessage(
            type=WebSocketMessageType.TYPING,
            data=data.model_dump(mode="json"),
        )
        await self.broadcast(data.chat_id, message)

    async def send_read(self, data: MessageReadData):
        message = WebSocketMessage(
            type=WebSocketMessageType.MESSAGE_READ,
            data=data.model_dump(mode="json"),
        )
        await self.broadcast(data.chat_id, message)

    async def send_user_joined(self, data: UserJoinedData):
        message = WebSocketMessage(
            type=WebSocketMessageType.USER_JOIN,
            data=data.model_dump(mode="json"),
        )
        await self.broadcast(data.chat_id, message)

    async def send_user_left(self, data: UserLeftData):
        message = WebSocketMessage(
            type=WebSocketMessageType.USER_LEFT,
            data=data.model_dump(mode="json"),
        )
        await self.broadcast(data.chat_id, message)

    async def send_error(self, chat_id: str, code: str, text: str):
        message = WebSocketMessage(
            type=WebSocketMessageType.ERROR,
            data=ErrorData(code=code, message=text).model_dump(),
        )
        await self.broadcast(chat_id, message)

    async def send_unread_update(self, chat_id: str, user_id: int, count: int):
        message = WebSocketMessage(
            type=WebSocketMessageType.UNREAD_UPDATE,
            data={"chat_id": chat_id, "count": count},
        )
        await self.send_to_user(user_id, message.model_dump(mode="json"))

    async def send_message_status(self, chat_id, message_id, delivered_to, read_by):
        message = WebSocketMessage(
            type=WebSocketMessageType.MESSAGE_STATUS,
            data={
                "message_id": message_id,
                "delivered_to": delivered_to,
                "read_by": read_by,
            },
        )
        await self.broadcast(chat_id, message)


manager = ConnectionManager()