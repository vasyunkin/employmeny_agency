from abc import abstractmethod
from typing import Protocol
from datetime import datetime

from src.domain.interview_slot import InterviewSlot


class InterviewSlotRepository(Protocol):
    @abstractmethod
    async def create(self, slot: InterviewSlot) -> InterviewSlot:
        ...

    @abstractmethod
    async def create_many(self, slots: list[InterviewSlot]) -> list[InterviewSlot]:
        ...

    @abstractmethod
    async def list_by_employer(self, employer_id: int) -> list[InterviewSlot]:
        ...

    @abstractmethod
    async def list_by_employer_and_period(
        self,
        employer_id: int,
        start_datetime: datetime,
        end_datetime: datetime
    ) -> list[InterviewSlot]:
        ...