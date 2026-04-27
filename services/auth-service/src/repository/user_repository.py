from sqlalchemy.ext.asyncio import AsyncSession
from src.models.models import User
from sqlalchemy import select, update


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, username: str, email: str, hashed_password: str, phone: str) -> User:
        user = User(username=username, email=email, hashed_password=hashed_password, phone=phone, is_active=True)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user


    async def get_by_id(self, user_id: int) -> User | None:
        return await self.db.get(User, user_id)

    async def get_by_phone(self, phone: str) -> User | None:
        result = await self.db.execute(select(User).where(User.phone == phone))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()


    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()




    async def exist_by_phone(self, phone: str) -> bool:
        result = await self.db.execute(select(User.id).where(User.phone == phone))
        return result.scalar_one_or_none() is not None


    async def exist_by_username(self, username: str) -> bool:
        result = await self.db.execute(select(User.id).where(User.username == username))
        return result.scalar_one_or_none() is not None

    async def exist_by_email(self, email: str) -> bool:
        result = await self.db.execute(select(User.id).where(User.email == email))
        return result.scalar_one_or_none() is not None




    async def set_email_verified(self, user_id: int) -> None:
        await self.db.execute(update(User).where(
            User.id == user_id)
            .values(is_email_verified=True)
        )
        await self.db.commit()


    async def update_password(self, user_id: int, hashed_password: str) -> None:
        await self.db.execute(update(User).where(
            User.id == user_id)
            .values(hashed_password=hashed_password)
        )
        await self.db.commit()


