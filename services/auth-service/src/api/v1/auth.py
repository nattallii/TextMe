from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.schemas import (
    UserCreate,
    UserLogin,
    TokenResponse,
    UserResponse,
    RefreshTokenRequest,
    LogoutRequest,
    EmailVerifyCode,
    ResetPasswordRequest,
    ForgotPasswordRequest,
)
from src.services.services import UserService
from src.db.deps import get_db, get_current_user_id

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
        data: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    return await UserService(db).register(data)


@router.post("/login", response_model=TokenResponse, status_code=200)
async def login(
        data: UserLogin,
        db: AsyncSession = Depends(get_db)
):
    return await UserService(db).login(data)


@router.post("/refresh", response_model=TokenResponse, status_code=200)
async def refresh_tokens(
        data: RefreshTokenRequest,
        db: AsyncSession = Depends(get_db)
):
    return await UserService(db).refresh_tokens(data.refresh_token)

@router.post("/logout", status_code=200)
async def logout(
        data: LogoutRequest,
        db: AsyncSession = Depends(get_db)
):
    return await UserService(db).logout(data.refresh_token)

@router.get("/me", response_model=UserResponse, status_code=200)
async def me(
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    return await UserService(db).get_me(user_id)

@router.post("/email/request-verification", status_code=200)
async def request_email_verification(
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    return await UserService(db).request_email_verification(user_id)

@router.post("/email/verify", status_code=200)
async def verify_email(
        data: EmailVerifyCode,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db),
):
    return await UserService(db).verify_email_code(user_id, data.code)


@router.post("/reset-password", status_code=200)
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    return await UserService(db).reset_password(
        token=data.token,
        new_password=data.new_password
    )

@router.post("/forgot-password", status_code=200)
async def forgot_password(
        data: ForgotPasswordRequest,
        db: AsyncSession = Depends(get_db),
):
    return await UserService(db).forgot_password(data.email)