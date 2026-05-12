from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from src.DAL.interfaces.user_repository import UserRepository
from src.domain.user import User


class SQLUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user: User) -> User:
        self._session.add(user)
        await self._session.flush()
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        return await self._session.get(User, user_id)

    async def get_by_login(self, user_login: str) -> User | None:
        stmt = select(User).where(User.user_login == user_login)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_login(self, user_login: str) -> bool:
        stmt = select(
            exists().where(User.user_login == user_login)
        )
        result = await self._session.execute(stmt)
        return result.scalar()
