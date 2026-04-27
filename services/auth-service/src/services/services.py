import secrets

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import datetime, timedelta, UTC
from src.security.verification import generate_verification_code

from src.repository.user_repository import UserRepository
from src.repository.email_verification_repository import EmailVerificationRepository
from src.repository.refresh_token_repository import RefreshTokenRepository
from src.repository.password_reset_repository import PasswordResetRepository

from src.security.password import hash_password, verify_password
from src.security.verification import generate_verification_code
from src.security.jwt import create_access_token, create_refresh_token
from src.schemas.schemas import UserCreate, UserLogin, TokenResponse
from src.messaging.publisher import publish_user_register
from src.email.email_service import send_email

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.email_repo = EmailVerificationRepository(db)
        self.refresh_repo = RefreshTokenRepository(db)
        self.reset_repo = PasswordResetRepository(db)

    async def register(self, data: UserCreate):

        if await self.user_repo.exist_by_phone(data.phone):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone already registered"
            )

        if await self.user_repo.exist_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        if await self.user_repo.exist_by_username(data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already registered"
            )

        user = await self.user_repo.create(
            username=data.username,
            phone=data.phone,
            email=data.email,
            hashed_password=hash_password(data.password)
        )

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        await self.refresh_repo.create_token(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )

        await self.db.commit()

        try:
            await publish_user_register(
                user_id=user.id,
                email=user.email,
                username=user.username,
                phone=user.phone,
            )
        except Exception as e:
            print(f"Failed to publish event: {e}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )



    async def login(self, data: UserLogin) -> TokenResponse:
        user = await self.user_repo.get_by_phone(data.phone)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect phone or password")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        await self.refresh_repo.create_token(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        await self.db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )


    async def logout(self, refresh_token: str):
        token_in_db = await self.refresh_repo.get_token(refresh_token)
        if not token_in_db:
            raise HTTPException(status_code=404, detail="Refresh token not found")

        if token_in_db.is_revoked:
            raise HTTPException(status_code=400, detail="Refresh token revoked")

        await self.refresh_repo.revoke_token(refresh_token)
        await self.db.commit()

        return {"message": "Logged out successfully"}



    async def get_me(self, user_id: int):
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user




    async def request_email_verification(self, user_id: int):
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user.is_email_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified")

        code = generate_verification_code()

        await self.email_repo.invalidate_active_code(user.id)
        await self.email_repo.create_verification_code(
            user_id=user.id,
            email=user.email,
            code=code,
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
        )

        await send_email(
            subject="Verify your email",
            recipients=[user.email],
            body=f"""
                <h3>TextMe Email Verification</h3>
                <p>Your verification code:</p>
                <h2>{code}</h2>
                <p>This code will expire in 10 minutes.</p>
                """
        )


        await self.db.commit()

        print(f"[EMAIL to {user.email}] Verification code: {code}")

        return {"message": "Verification code sent"}




    async def verify_email_code(self, user_id: int, code: str):
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user.is_email_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified")


        verification = await self.email_repo.get_latest_active_code(user.id)
        if not verification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verification code not found")

        if verification.is_used:
            raise HTTPException(status_code=400, detail="Verification code already used")

        if verification.expires_at < datetime.now(UTC):
            raise HTTPException(status_code=400, detail="Email expired")

        if verification.code != code:
            raise HTTPException(status_code=400, detail="Incorrect code")

        await self.email_repo.mark_code_used(verification.id)
        await self.user_repo.set_email_verified(user.id)


        await self.db.commit()
        print(f"[VERIFY EMAIL] user={user.id}, code={code}")
        return {"message": "Email verified successfully"}



    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        token_in_db = await self.refresh_repo.get_token(refresh_token)
        if not token_in_db:
            raise HTTPException(status_code=404, detail="Refresh token not found")

        if token_in_db.is_revoked:
            raise HTTPException(status_code=400, detail="Refresh token revoked")

        if token_in_db.expires_at < datetime.now(UTC):
            raise HTTPException(status_code=400, detail="Refresh token expired")

        user = await self.user_repo.get_by_id(token_in_db.user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=403, detail="Inactive user")

        new_access_token = create_access_token(user.id)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,
        )

    async def forgot_password(self, email: str):
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        token = secrets.token_urlsafe(32)

        await self.reset_repo.invalidate_active_tokens(user.id)
        await self.reset_repo.create_token(
            user_id=user.id,
            token=token,
            expires_at=datetime.now(UTC) + timedelta(minutes=15),
        )

        await self.db.commit()

        print(f"[PASSWORD RESET] Email: {user.email}, token: {token}")

        return {"message": "Password reset token sent"}


    async def reset_password(self, token: str, new_password: str):
        reset = await self.reset_repo.get_active_token(token)
        if not reset:
            raise HTTPException(status_code=404, detail="Reset token not found")

        if reset.is_used:
            raise HTTPException(status_code=400, detail="Reset token already used")

        if reset.expires_at < datetime.now(UTC):
            raise HTTPException(status_code=400, detail="Reset token expired")

        user = await self.user_repo.get_by_id(reset.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await self.user_repo.update_password(
            user_id=user.id,
            hashed_password=hash_password(new_password),
        )

        await self.reset_repo.mark_token_used(reset.id)

        await self.refresh_repo.revoke_all_user_tokens(user.id)
        await self.db.commit()
        return {"message": "Password reset"}