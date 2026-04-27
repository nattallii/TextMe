from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from src.models.models import RefreshToken
from sqlalchemy import select, update


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def create_token(self, user_id: str, token: str, expires_at: datetime) -> RefreshToken:
        entity = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            is_revoked=False,
        )
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def get_token(self, token: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()


    async def revoke_token(self, token: str) -> RefreshToken | None:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.token == token)
            .values(is_revoked=True)
        )
        await self.db.commit()

    async def revoke_all_user_tokens(self, user_id: int) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(is_revoked=True)
        )
        await self.db.commit()




