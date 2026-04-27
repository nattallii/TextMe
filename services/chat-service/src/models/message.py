import uuid
from beanie import Document
from datetime import datetime, timezone
from pydantic import Field

class Message(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chat_id: str
    sender_id: int
    content: str
    is_read: bool = False
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "messages"
        indexes = [
            "chat_id",
            "sender_id",
            [("chat_id", 1), ("created_at", -1)],
        ]