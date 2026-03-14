from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.repository.repository import UserRepository
from src.security.password import hash_password, verify_password
from src.security.jwt import create_access_token, create_refresh_token
from src.schemas.schemas import UserCreate, UserLogin, TokenResponse


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, data: UserCreate):
        if await self.repo.exist_by_phone(data.phone):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already registered")

        user = await self.repo.create(
            username=data.username,
            phone=data.phone,
            hashed_password=hash_password(data.password)
        )

        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id)
        )

    async def login(self, data: UserLogin) -> TokenResponse:
        user = await self.repo.get_by_phone(data.phone)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect phone or password")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id)
        )