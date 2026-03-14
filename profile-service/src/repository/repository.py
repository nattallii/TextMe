from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.models import UserProfile


class ProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_profile(self, user_id: int, username: str, phone: str, bio: str | None = None) -> UserProfile:
        profile = UserProfile(
            user_id=user_id,
            username=username,
            phone=phone,
            bio=bio,
        )
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def get_by_id(self, profile_id: int) -> UserProfile | None:
        result = await self.db.execute(select(UserProfile).where(UserProfile.id == profile_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> UserProfile | None:
        result = await self.db.execute(select(UserProfile).where(UserProfile.username == username))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> UserProfile | None:
        result = await self.db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> UserProfile | None:
        result = await self.db.execute(select(UserProfile).where(UserProfile.phone == phone))
        return result.scalar_one_or_none()

    async def delete_profile(self, profile: UserProfile) -> None:
        await self.db.delete(profile)
        await self.db.commit()