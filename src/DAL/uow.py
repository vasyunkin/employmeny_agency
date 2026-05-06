from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from src.DAL.interfaces.user_repository import UserRepository
from src.DAL.repositories.sql_user_repository import SQLUserRepository


class SQLAlchemyUnitOfWork:
    """Реализация Unit of Work на SQLAlchemy"""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory
        self._session: AsyncSession | None = None
        self.user: UserRepository | None = None

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        self._session = self.session_factory()
        self.user = SQLUserRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self.close()

    async def commit(self) -> None:
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session:
            await self._session.rollback()

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None
            self.user = None


# Удобный контекстный менеджер
@asynccontextmanager
async def unit_of_work(
    session_factory: async_sessionmaker[AsyncSession]
) -> AsyncGenerator[SQLAlchemyUnitOfWork, None]:
    """
    Использование:
    async with unit_of_work(session_factory) as uow:
        user = await uow.user.create(...)
        await uow.commit()  # не обязательно, если используешь __aenter__/__aexit__
    """
    uow = SQLAlchemyUnitOfWork(session_factory)
    async with uow:
        yield uow