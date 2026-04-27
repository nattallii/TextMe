from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.repository import ProfileRepository
from src.schemas.schemas import ProfileCreate, ProfileOut


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.repo = ProfileRepository(db)

    async def create_profile(self, user_id: int, data: ProfileCreate) -> ProfileOut:

        existing_profile = self.repo.exist_profile(user_id)
        if existing_profile:
            raise HTTPException(status_code=409, detail="Profile already exists")

        profile = await self.repo.create_profile(
            user_id=user_id,
            username=data.username,
            phone=data.phone,
            bio=data.bio,
        )


        return ProfileOut.model_validate(profile)


    async def delete_profile(self, user_id: int, profile_id: int) -> None:
        profile = await self.repo.get_profile_by_id(profile_id=profile_id, user_id=user_id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        await self.repo.delete_profile(profile)