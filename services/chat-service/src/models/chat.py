import uuid
from enum import Enum
from typing import Optional
from beanie import Document
from datetime import datetime, timezone
from pydantic import Field

class ChatType(str, Enum):
    PRIVATE = "private"
    GROUP = "group"


class Chat(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    type: ChatType = ChatType.PRIVATE
    members: list[int] = Field(default_factory=list)
    created_by: int
    name: Optional[str] = None
    dm_key: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    is_deleted: bool = False

    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None

    class Settings:
        name = "chats"
        indexes = [
            "dm_key",
            "members",
            "created_by",
            [("created_at", -1)],
        ]

class ChatPermissionModel(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chat_id: str
    user_id: int

    can_send_messages: bool = True
    can_change_permissions: bool = False
    can_remove_members: bool = False
    can_remove_other_messages: bool = False

    class Settings:
        name = "chat_permissions"
        indexes = [
            "id",
            "chat_id",
            "user_id",
            [("chat_id", 1), ("user_id", 1)],
        ]


class ChatReadState(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    chat_id: str
    user_id: int

    last_read_message_id: Optional[str] = None

    class Settings:
        name = "chat_read_states"
        indexes = [
            [("chat_id", 1), ("user_id", 1)],
        ]