from pydantic import BaseModel, Field
from datetime import datetime



class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class MessageOut(BaseModel):
    id: str
    chat_id: str
    sender_id: int
    content: str
    created_at: datetime




