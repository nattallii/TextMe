from pydantic import BaseModel
from typing import Any
from enum import Enum
from datetime import datetime


class WebSocketMessageType(str, Enum):
    NEW_MESSAGE = "new_message"
    MESSAGE_READ = "message_read"
    MESSAGE_DELETE = "message_delete"
    TYPING= "typing"
    USER_JOIN = "user_join"
    USER_LEFT = "user_left"
    ERROR = "error"


class WebSocketMessage(BaseModel):
    type: WebSocketMessageType
    data: dict[str, Any]


class NewMessageData(BaseModel):
    id: str
    chat_id: str
    sender_id: int
    content: str
    created_at: datetime


class MessageReadData(BaseModel):
    chat_id: str
    message_id: str
    user_id: int

class TypingData(BaseModel):
    chat_id: str
    user_id: int
    is_typing: bool


class UserJoinedData(BaseModel):
    chat_id: str
    user_id: int


class UserLeftData(BaseModel):
    chat_id: str
    user_id: int

class ErrorData(BaseModel):
    code: str
    message: str

