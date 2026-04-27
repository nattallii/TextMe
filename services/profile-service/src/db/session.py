from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.security.config import settings

engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
