from abc import abstractmethod
from typing import Protocol

from src.DAL.interfaces.user_repository import UserRepository


class UnitOfWork(Protocol):
    user: UserRepository

    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def rollback(self) -> None:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...