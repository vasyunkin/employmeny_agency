from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from typing import AsyncGenerator

from src.main.config import PostgresConfig


postgres_config = PostgresConfig()
DATABASE_URL = postgres_config.build_dsn()


engine = create_async_engine(
    DATABASE_URL,
    echo=postgres_config.enable_logging,
    future=True,
)


async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Предоставляет сессию БД для эндпоинтов"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()