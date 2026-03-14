import uuid

from beanie import Document
from datetime import datetime, timezone
from pydantic import Field

class Chat(Document):
    chat_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "private"
    members: list[int]
    dm_key: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "chats"
        indexes = [
            "dm_key",
            "members"
        ]