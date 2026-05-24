from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from pydantic import model_validator

class Attachment(BaseModel):
    url: str
    filename: str
    content_type: str
    size: int



class MessageCreate(BaseModel):
    content: str | None = Field(
        default=None,
        max_length=5000,
    )
    attachments: list[Attachment] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_message(self):
        if not self.content and not self.attachments:
            raise ValueError(
                "Message must contain content or attachment"
            )

        return self


class MessageOut(BaseModel):
    id: str

    chat_id: str
    sender_id: int

    content: str

    is_deleted: bool
    is_edited: bool

    created_at: datetime
    updated_at: datetime | None = None

    attachments: list[Attachment] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)



class MessageUpdate(BaseModel):
    content: str

    model_config = ConfigDict(extra="forbid")



