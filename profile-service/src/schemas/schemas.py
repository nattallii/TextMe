from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProfileBase(BaseModel):
    username: str
    phone: str
    bio: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)