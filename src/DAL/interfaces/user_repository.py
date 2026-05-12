from abc import abstractmethod
from typing import Protocol

from src.domain.user import User


class UserRepository(Protocol):
    @abstractmethod
    async def create(self, user: User) -> User:
        ...

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        ...

    @abstractmethod
    async def get_by_login(self, user_login: str) -> User | None:
        ...

    @abstractmethod
    async def exists_by_login(user_login: str) -> bool:
        ...