from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from src.models.models import PasswordResetToken


class PasswordResetRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_token(self, user_id: int, token: str, expires_at: datetime) -> PasswordResetToken:
        entity = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            is_used=False,
        )
        self.db.add(entity)
        await self.db.flush()
        return entity

    async def get_active_token(self, token: str) -> PasswordResetToken | None:
        result = await self.db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token == token,
                PasswordResetToken.is_used == False,
            )
        )
        return result.scalar_one_or_none()

    async def mark_token_used(self, token_id: int) -> None:
        await self.db.execute(
            update(PasswordResetToken)
            .where(PasswordResetToken.id == token_id)
            .values(is_used=True)
        )

    async def invalidate_active_tokens(self, user_id: int) -> None:
        await self.db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.is_used == False,
            )
            .values(is_used=True)
        )



