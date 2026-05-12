from abc import abstractmethod
from typing import Protocol

from src.domain.match import Match


class MatchRepository(Protocol):
    @abstractmethod
    async def create(self, match: Match) -> Match:
        ...

    @abstractmethod
    async def update(self, match: Match) -> None:
        ...

    @abstractmethod
    async def delete(self, match_id: int) -> None:
        ...

    @abstractmethod
    async def get_by_id(self, match_id: int) -> Match | None:
        ...

    @abstractmethod
    async def exists(self, vacancy_id: int, resume_id: int) -> bool:
        ...

    @abstractmethod
    async def list_by_recruiter(self, recruiter_id: int) -> list[Match]:
        ...

    @abstractmethod
    async def list_by_resume(self, resume_id: int) -> list[Match]:
        ...

    @abstractmethod
    async def list_by_vacancy(self, vacancy_id: int) -> list[Match]:
        ...

    @abstractmethod
    async def search(self) -> list[Match]:
        ...