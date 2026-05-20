from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional


class ProfileBase(BaseModel):
    username: str
    phone: str
    email: EmailStr
    bio: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    bio: Optional[str] = None

    model_config = ConfigDict(extra="forbid")

class ProfileOut(ProfileBase):
    id: int
    user_id: int

    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)