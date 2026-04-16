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