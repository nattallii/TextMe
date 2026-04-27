from pydantic import BaseModel, field_validator, Field, model_validator, EmailStr
import re


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    phone: str
    email: EmailStr

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Only letters, digits and underscores allowed.")
        return v.lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"\s+", "", v)
        if not re.match(r"^\+?[0-9]{10,15}$", cleaned):
                raise ValueError("Incorrect format. Example: +380991234567")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Must contain numbers")
        if not re.search(r"[!@#$%^&*]", v):
            raise ValueError("Must contain !@#$%^&*")
        return v


class UserLogin(BaseModel):
    phone: str
    password: str



class UserResponse(UserBase):
    id: int
    phone: str
    email: EmailStr
    is_active: bool
    is_email_verified: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class EmailVerifyCode(BaseModel):
    code: str = Field(min_length=6, max_length=6)


class LogoutRequest(BaseModel):
    refresh_token: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Must contain numbers")
        if not re.search(r"[!@#$%^&*]", v):
            raise ValueError("Must contain !@#$%^&*")
        return v