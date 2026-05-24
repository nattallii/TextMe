import uuid
from beanie import Document
from datetime import datetime, timezone
from pydantic import Field
from src.schemas.message import Attachment

class Message(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chat_id: str
    sender_id: int

    content: str

    is_read: bool = False
    is_deleted: bool = False
    is_edited: bool = False

    delivered_to: list[int] = Field(default_factory=list)
    read_by: list[int] = Field(default_factory=list)

    updated_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    attachments: list[Attachment] = Field(default_factory=list)

    class Settings:
        name = "messages"
        indexes = [
            "chat_id",
            "sender_id",
            [("chat_id", 1), ("created_at", -1)],
        ]