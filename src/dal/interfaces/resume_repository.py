from abc import abstractmethod
from typing import Protocol, Optional

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
    async def deactivate(self, resume_id: int) -> None:
        ...

    @abstractmethod
    async def exists_similar(
        self,
        applicant_id: int,
        desired_position: str
    ) -> bool:
        ...

    @abstractmethod
    async def search(
            self,
            desired_position: Optional[str] = None,
            min_experience: Optional[int] = None,
            is_active: Optional[bool] = True,
            limit: int = 50,
            offset: int = 0
    ) -> list[Resume]:
        ...