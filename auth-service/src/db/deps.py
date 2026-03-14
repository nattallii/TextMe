from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import AsyncSessionLocal
from src.security.jwt import decode_token
from src.models.models import User
from src.repository.repository import UserRepository

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")



async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            session.rollback()
            raise



async def get_current_user(token: str = Depends(oauth2_scheme), db : AsyncSession = Depends(get_db)) -> User:
    print(f"TOKEN: {token}")
    try:
        user_id = decode_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await UserRepository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
            raise HTTPException(status_code=403, detail="Inactive user")

    return user