from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime



class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class MessageOut(BaseModel):
    id: str

    chat_id: str
    sender_id: int

    content: str

    is_deleted: bool
    is_edited: bool

    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

class MessageUpdate(BaseModel):
    content: str

    model_config = ConfigDict(extra="forbid")



