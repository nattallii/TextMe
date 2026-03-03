from beanie import Document
from datetime import datetime, timezone
from pydantic import Field

class Message(Document):
    chat_id: str
    sender_id: int
    text: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "messages"