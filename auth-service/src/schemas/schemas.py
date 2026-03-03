from pydantic import BaseModel, field_validator, Field, model_validator
import re


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    phone: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Тільки літери, цифри та _")
        return v.lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"\s+", "", v)
        if not re.match(r"^\+?[0-9]{10,15}$", cleaned):
            raise ValueError("Невірний формат. Приклад: +380991234567")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Має містити велику літеру")
        if not re.search(r"[0-9]", v):
            raise ValueError("Має містити цифру")
        if not re.search(r"[!@#$%^&*]", v):
            raise ValueError("Має містити спецсимвол !@#$%^&*")
        return v


class UserLogin(BaseModel):
    phone: str
    password: str

    @model_validator(mode="after")
    def check_fields(self) -> "UserLogin":
        if not self.phone or not self.password:
            raise ValueError("Телефон і пароль обовʼязкові")
        return self


class UserResponse(UserBase):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"