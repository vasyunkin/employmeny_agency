from abc import abstractmethod
from typing import Protocol

from src.domain.interview import Interview


class InterviewRepository(Protocol):
    @abstractmethod
    async def create(self, interview: Interview) -> Interview:
        ...

    @abstractmethod
    async def get_by_id(self, interview_id: int) -> Interview | None:
        ...

    @abstractmethod
    async def get_by_match_id(self, match_id: int) -> Interview | None:
        ...

    @abstractmethod
    async def exists_by_slot(self, slot_id: int) -> bool:
        ...

    @abstractmethod
    async def update_applicant_feedback(
        self,
        interview_id: int,
        feedback: bool
    ) -> None:
        ...

    @abstractmethod
    async def update_employer_feedback(
        self,
        interview_id: int,
        feedback: bool
    ) -> None:
        ...