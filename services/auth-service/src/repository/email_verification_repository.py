from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from src.models.models import EmailVerificationCode


class EmailVerificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db



    async def create_verification_code(self, user_id: int, email: str, code: str, expires_at):
        entity = EmailVerificationCode(
            user_id=user_id,
            email=email,
            code=code,
            expires_at=expires_at
        )

        self.db.add(entity)
        await self.db.flush()

        return entity




    async def get_latest_active_code(self, user_id: int):
        result = await self.db.execute(
            select(EmailVerificationCode).where(
    EmailVerificationCode.user_id == user_id,
                EmailVerificationCode.is_used == False

            ).order_by(EmailVerificationCode.created_at.desc())
        )
        return result.scalar_one_or_none()




    async def invalidate_active_code(self, user_id: int):
        await self.db.execute(
            update(EmailVerificationCode).where(
    EmailVerificationCode.user_id == user_id,
                EmailVerificationCode.is_used == False

            ).values(is_used=True)
        )


    async def mark_code_used(self, code_id: int):
        await self.db.execute(
            update(EmailVerificationCode).where(
    EmailVerificationCode.id == code_id,
                EmailVerificationCode.is_used == False

            ).values(is_used=True)
        )
