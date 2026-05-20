import uuid
from beanie import Document
from datetime import datetime, timezone
from pydantic import Field


class Contact(Document):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    owner_id: int
    contact_id: int

    label: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "contacts"
        indexes = [
            [("owner_id", 1), ("contact_id", 1)]
        ]

