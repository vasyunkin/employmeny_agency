from abc import abstractmethod
from typing import Protocol

from src.domain.resume import Resume


class ResumeRepository(Protocol):
    @abstractmethod
    async def create(self, resume: Resume) -> Resume:
        ...

    @abstractmethod
    async def get_by_id(self, resume_id: int) -> Resume | None:
        ...

    @abstractmethod
    async def list_by_applicant(self, applicant_id: int) -> list[Resume]:
        ...

    @abstractmethod
    async def exists_similar(
        self,
        applicant_id: int,
        desired_position: str
    ) -> bool:
        ...

    @abstractmethod
    async def search(self) -> list[Resume]:
        ...