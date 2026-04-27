from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional


class ProfileBase(BaseModel):
    username: str
    phone: str
    email: EmailStr
    bio: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    username: Optional[str] = None
    bio: Optional[str] = None

    model_config = ConfigDict(extra="forbid")

class ProfileOut(ProfileBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)