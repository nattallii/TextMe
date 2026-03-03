from sqlalchemy.ext.asyncio import AsyncSession
from src.models.models import User
from sqlalchemy import select


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_phone(self, phone: str) -> User | None:
        result = await self.db.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    async def exist_by_phone(self, phone: str) -> bool:
        result = await self.db.execute(select(User.id).where(User.phone == phone))
        return result.scalar_one_or_none() is not None


    async def exist_by_username(self, username: str) -> bool:
        result = await self.db.execute(select(User.id).where(User.username == username))
        return result.scalar_one_or_none() is not None

    async def create(self, username: str, hashed_password: str, phone: str) -> User:
        user = User(username=username, hashed_password=hashed_password, phone=phone)
        self.db.add(user)
        await self.db.flush()
        return user

    async def get_by_id(self, user_id: str) -> User | None:
        return await self.db.get(User, user_id)