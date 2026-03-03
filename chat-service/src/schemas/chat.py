from pydantic import BaseModel
from datetime import datetime


class CreateChat(BaseModel):
    member_id: int


class ChatOut(BaseModel):
    id: str
    members: list[int]
    created_at: datetime

