from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, model_validator
from datetime import datetime, timezone


class ChatType(str, Enum):
    PRIVATE = "private"
    GROUP = "group"


class CreateChat(BaseModel):
    type: ChatType
    member_ids: List[int] = Field(default_factory=list)
    name: Optional[str] = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def validate_chat(self):
        if self.type == ChatType.PRIVATE and len(self.member_ids) != 1:
            raise ValueError("Private chat must have exactly 1 other user")

        if self.type == ChatType.GROUP and len(self.member_ids) < 2:
            raise ValueError("Group chat must have at least 2 members")

        return self



class ChatOut(BaseModel):
    id: str
    type: ChatType
    members: list[int]
    name: Optional[str] = None

    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None

    created_by: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class AddMembersSchema(BaseModel):
    member_ids: List[int] = Field(min_length=1)


class RemoveMemberSchema(BaseModel):
    user_id: int



class ChatWithUnread(ChatOut):
    unread_count: int


class UpdatePermissions(BaseModel):
    can_send_messages: bool = True
    can_add_members: bool = False
    can_remove_members: bool = False
    can_delete_messages: bool = False