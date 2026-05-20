from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.repository import ProfileRepository
from src.schemas.schemas import ProfileCreate, ProfileOut, ProfileUpdate


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.repo = ProfileRepository(db)

    async def create_profile(self, user_id: int, data: ProfileCreate) -> ProfileOut:

        existing_profile = await self.repo.exist_profile(user_id)
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


    async def get_profile_by_phone(self, phone: str) -> ProfileOut:
        profile = await self.repo.get_by_phone(phone)

        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        return profile

    async def get_by_id(self, user_id: int) -> ProfileOut | None:
        profile = await self.repo.get_by_user_id(user_id)
        return profile

    async def get_user_by_id(self, user_id: int):
        return await self.repo.get_by_user_id(user_id)

    async def update_profile(
            self,
            user_id: int,
            data: ProfileUpdate
    ) -> ProfileOut:

        profile = await self.repo.get_by_user_id(user_id)

        if not profile:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )

        update_data = data.model_dump(exclude_unset=True)

        updated_profile = await self.repo.update_profile(
            profile,
            update_data
        )

        return ProfileOut.model_validate(updated_profile)


