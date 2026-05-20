from fastapi import APIRouter, Depends, Response, status, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.deps import get_db
from src.schemas.schemas import ProfileCreate, ProfileOut, ProfileUpdate
from src.repository.repository import ProfileRepository
from src.services.services import ProfileService
from src.security.jwt import get_current_user_id
from src.storage import upload_avatar

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("/", response_model=ProfileOut)
async def create_profile(
    data: ProfileCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return await ProfileService(db).create_profile(user_id, data)

@router.get("/", response_model=ProfileOut)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id),
):
    repo = ProfileRepository(db)
    user = await repo.get_by_user_id(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user

@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    await ProfileService(db).delete_profile(user_id, profile_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.patch("/", response_model=ProfileOut)
async def update_profile(
    data: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = ProfileService(db)
    return await service.update_profile(user_id, data)


@router.patch("/avatar")
async def update_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = ProfileService(db)

    print("USER ID:", user_id)

    profile = await service.get_by_id(user_id)

    print("PROFILE:", profile)

    if not profile:
        raise HTTPException(404, "Profile not found")

    avatar_url = await upload_avatar(file)

    profile.avatar_url = avatar_url

    await db.commit()
    await db.refresh(profile)

    return {
        "avatar_url": avatar_url
    }