from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.deps import get_db
from src.schemas.schemas import ProfileCreate, ProfileOut
from src.services.services import ProfileService
from src.security.jwt import get_current_user_id


router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("/", response_model=ProfileOut)
async def create_profile(
    data: ProfileCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    return await ProfileService(db).create_profile(user_id, data)