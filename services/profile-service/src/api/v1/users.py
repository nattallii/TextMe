from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import unquote
from src.db.deps import get_db
from src.schemas.schemas import ProfileOut
from src.services.services import ProfileService

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/search", response_model=ProfileOut)
async def search_contact(
    phone: str,
    db: AsyncSession = Depends(get_db),
):
    phone = unquote(phone)

    service = ProfileService(db)
    user = await service.get_profile_by_phone(phone)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/{user_id}", response_model=ProfileOut)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = ProfileService(db)

    user = await service.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user