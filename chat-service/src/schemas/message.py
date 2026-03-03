from pydantic import BaseModel
from datetime import datetime



class MessageCreate(BaseModel):
    text: str


class MessageOut(BaseModel):
    id: str
    chat_id: str
    sender_id: int
    text: str
    is_read: bool
    created_at: datetime


