from beanie import Document
from datetime import datetime, timezone
from pydantic import Field

class Chat(Document):
    members: list[int]
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "chats"