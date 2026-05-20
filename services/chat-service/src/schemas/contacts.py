from pydantic import BaseModel


class ProfileShort(BaseModel):
    id: int
    username: str
    phone: str
    avatar_url: str | None = None

class AddContactRequest(BaseModel):
    phone: str
    label: str | None = None


class UpdateLabel(BaseModel):
    label: str


class ContactOut(BaseModel):
    id: str
    label: str | None
    user: ProfileShort

    class Config:
        from_attributes = True