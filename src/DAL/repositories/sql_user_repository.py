from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.DAL.interfaces.user_repository import UserRepository
from src.DAL.tables.user_orm import UserORM
from src.DAL.mappers.user_mapper import to_domain, from_domain
from src.domain.user import User


class SQLUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session


    async def create(self, user: User) -> User:
        user_orm = from_domain(user)

        self._session.add(user_orm)
        await self._session.flush()
        return to_domain(user_orm)


    async def get_by_id(self, user_id: int) -> User | None:
        result = await self._session.execute(
            select(UserORM).where(UserORM.user_id == user_id)
        )

        user_orm = result.scalar_one_or_none()
        return to_domain(user_orm) if user_orm else None