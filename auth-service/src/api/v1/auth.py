from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.schemas import UserLogin, UserCreate, TokenResponse
from src.services.services import UserService
from src.db.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await UserService(db).register(data)


@router.post("/login", response_model=TokenResponse, status_code=200)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await UserService(db).login(data)