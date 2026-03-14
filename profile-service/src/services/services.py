from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.repository.repository import ProfileRepository
from src.schemas.schemas import ProfileBase, ProfileCreate, ProfileOut


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.repo = ProfileRepository(db)

    async def create_profile(self, user_id: int, data: ProfileCreate) -> ProfileOut:
        # existing_profile = self.repo.get_by_user_id(user_id)
        # if existing_profile:
        #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Profile already exists")

        profile = await self.repo.create_profile(
            user_id=user_id,
            username=data.username,
            phone=data.phone,
            bio=data.bio,
        )
        return ProfileOut.model_validate(profile)
