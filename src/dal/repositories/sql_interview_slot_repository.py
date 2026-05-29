from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dal.interfaces.interview_slot_repository import InterviewSlotRepository
from src.domain.interview_slot import InterviewSlot


class SqlInterviewSlotRepository(InterviewSlotRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, slot: InterviewSlot) -> InterviewSlot:
        self._session.add(slot)
        await self._session.flush()
        return slot

    async def create_many(self, slots: list[InterviewSlot]) -> list[InterviewSlot]:
        self._session.add_all(slots)
        await self._session.flush()
        return slots

    async def list_by_employer(self, employer_id: int) -> list[InterviewSlot]:
        stmt = select(InterviewSlot).where(
            InterviewSlot.employer_id == employer_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_employer_and_period(
        self,
        employer_id: int,
        start_datetime: datetime,
        end_datetime: datetime
    ) -> list[InterviewSlot]:
        stmt = select(InterviewSlot).where(
            (InterviewSlot.employer_id == employer_id) &
            (InterviewSlot.slot_datetime >= start_datetime) &
            (InterviewSlot.slot_datetime < end_datetime)
        ).order_by(InterviewSlot.slot_datetime)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())