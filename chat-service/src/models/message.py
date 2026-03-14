from beanie import Document
from datetime import datetime, timezone
from pydantic import Field

class Message(Document):
    chat_id: str
    sender_id: int
    text: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "messages"
        indexes = [
            "conversation_id",
            [("conversation_id", 1), ("created_at", -1)]
        ]